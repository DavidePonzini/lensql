from . import html

from .. import server
from ..sql_errors import SQLException

from enum import Enum
from IPython.display import display, HTML
import ipywidgets as widgets
import pandas as pd
from dav_tools.chatgpt import MessageRole

CHAT_ID = 0
MSG_ID = 0

class Buttons(Enum):
    pass
    # SUCCESS_WRONG_OUTPUT = 'The output is not what I expected'
    # MANUAL_PROMPT = 'Other'

class ResultButtons(Buttons):
    DESCRIBE = 'Describe query'
    EXPLAIN = 'Explain query'

class ErrorButtons(Buttons):
    EXPLAIN = 'Explain error'
    EXAMPLE = 'Show example'
    LOCATE = 'Where to look'
    FIX = 'Suggest fix'


class Message:
    '''Represents a message in the chat.'''
    def __init__(self, role: MessageRole, content: str):
        global MSG_ID
        MSG_ID += 1
        self.msg_id = MSG_ID
        self.role = role
        self.content = content
        self.html = html.Message(role, content, self.msg_id)


class Chat:
    '''Generic chat for displaying messages and interacting with the user.'''
    def __init__(self):
        global CHAT_ID
        CHAT_ID += 1
        self.chat_id = CHAT_ID
        self.messages: list[Message] = []
        self.thinking_msg = None

        self.output_widget = widgets.Output()  # Capture output in Jupyter cell

    @property
    def last_message_id(self) -> int:
        if len(self.messages) == 0:
            return -1
        return self.messages[-1].msg_id

    def show(self) -> None:
        display(self.output_widget)  # Ensure output appears inside the correct cell

        chat_html = html.Chat(self.chat_id)
        self.display_html(chat_html)

    def display_html(self, content: str):
        with self.output_widget:
            display(HTML(str(content)))

    def display_box(self, content: list[widgets.Widget]):
        with self.output_widget:
            display(widgets.HBox(content))

    def show_message(self, role: MessageRole, text: str) -> Message:
        message = Message(role, text)
        self.messages.append(message)

        message_html = str(message.html)
        message_html = message_html.replace('`', '\\`') #.replace('\n', '<br>')

        append_script = f'''
            <script>
                var target = document.getElementById('chat{self.chat_id}');
                target.insertAdjacentHTML('beforeend', `{message_html}`);
                target.scrollTop = target.scrollHeight;
            </script>
        '''

        self.display_html(append_script)
        return message
    
    def delete_message(self, msg_id: int) -> None:
        delete_script = f'''
            <script>
                var target = document.getElementById('msg{msg_id}');
                target.remove();
            </script>
        '''
        self.display_html(delete_script)

    def is_thiking(self) -> bool:
        '''Returns whether the assistant is currently thinking.'''
        return self.thinking_msg is not None

    def start_thinking(self) -> None:
        '''Displays a `Thinking...` message in the chat.'''
        if self.is_thiking():
            self.stop_thinking()

        self.thinking_msg = self.show_message(MessageRole.ASSISTANT, 'Thinking...')

    def stop_thinking(self) -> None:
        '''Removes the `Thinking...` message from the chat.'''
        if not self.is_thiking():
            return
        
        self.delete_message(self.thinking_msg.msg_id)
        self.thinking_msg = None

    def get_input(self, cb):
        """Creates a text input field for the user to type in."""
        text_input = widgets.Text(placeholder='Type here...', layout=widgets.Layout(width='100%'))
        send_button = widgets.Button(description='Send')

        # Define the on_submit event
        def on_submit(b):
            user_text = text_input.value.strip()
            if user_text:
                cb(user_text)
                text_input.close()
                send_button.close()
        # -- End of on_submit event --

        text_input.on_submit(on_submit)
        send_button.on_click(on_submit)

        self.display_box([text_input, send_button])

class CodeChat(Chat):
    '''Chat related to a specific code snippet.'''
    def __init__(self, query_id : int, code: str, data):
        super().__init__()

        self.query_id = query_id
        self.code = code
        self.data = data


class ResultChat(CodeChat):
    '''Chat related to a specific code snippet that has returned a result.'''
    def __init__(self, query_id: int, code: str, result: pd.DataFrame):
        super().__init__(query_id, code, data=result)

    def show(self):
        super().show()

        self.show_buttons()

    def show_buttons(self):
        options = [option.value for option in ResultButtons]
        buttons = [widgets.Button(description=option) for option in options]

        buttons[0].layout.margin = '2px 2px 2px 62px'
        for button in buttons[1:]:
            button.layout.margin = '2px 2px 2px 2px'

        # Define the on_click event
        def on_button_click(b):
            button_text = b.description

            for button in buttons:
                button.close()

            self.show_message(MessageRole.USER, button_text)
            self.start_thinking()

            if button_text == ResultButtons.DESCRIBE.value:
                response = server.describe_my_query(self.query_id, self.chat_id, self.last_message_id)
            elif button_text == ResultButtons.EXPLAIN.value:
                response = server.explain_my_query(self.query_id, self.chat_id, self.last_message_id)
            else:
                response = 'Action not implemented yet.'

            self.stop_thinking()
            self.show_message(MessageRole.ASSISTANT, response)
            self.show_buttons()
        # -- End of on_button_click event --

        # Assign on_click event to each button
        for button in buttons:
            button.on_click(on_button_click)

        self.display_box(buttons)


class ErrorChat(CodeChat):
    '''Chat related to a specific code snippet that has returned an error.'''
    def __init__(self, query_id: int, code, exception: Exception):
        super().__init__(query_id, code, data=SQLException(exception))
        
    def show(self):
        super().show()

        message = html.exception_to_html(self.data)
        self.show_message(MessageRole.ASSISTANT, message)
        self.show_buttons()

    def show_buttons(self):
        """Creates a set of buttons for the user to choose from."""
        options = [option.value for option in ErrorButtons]
        buttons = [widgets.Button(description=option) for option in options]
        
        buttons[0].layout.margin = '2px 2px 2px 62px'
        for button in buttons[1:]:
            button.layout.margin = '2px 2px 2px 2px'

        # Define the on_click event
        def on_button_click(b):
            button_text = b.description

            for button in buttons:
                button.close()

            self.show_message(MessageRole.USER, button_text)
            self.start_thinking()

            if button_text == ErrorButtons.EXPLAIN.value:
                response = server.explain_error_message(self.query_id, str(self.data), self.chat_id, self.last_message_id)
            elif button_text == ErrorButtons.EXAMPLE.value:
                response = server.provide_error_example(self.query_id, str(self.data), self.chat_id, self.last_message_id)
            elif button_text == ErrorButtons.LOCATE.value:
                response = server.locate_error_cause(self.query_id, str(self.data), self.chat_id, self.last_message_id)
            elif button_text == ErrorButtons.FIX.value:
                response = server.fix_query(self.query_id, str(self.data), self.chat_id, self.last_message_id)
            else:
                response = 'Action not implemented yet.'

            self.stop_thinking()
            self.show_message(MessageRole.ASSISTANT, response)
            self.show_buttons()

        # -- End of on_button_click event --

        # Assign on_click event to each button
        for button in buttons:
            button.on_click(on_button_click)

        self.display_box(buttons)