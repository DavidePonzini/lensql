from enum import Enum
from IPython import get_ipython
from IPython.display import display, HTML
import utils
import html
import ipywidgets as widgets

CHAT_ID = 0
CSS = utils.load_file('style.css')

def show_result(result, shell=get_ipython()) -> None:
    display(result)

def show_error(exception: Exception, shell=get_ipython()) -> None:
    """Creates a new chat instance for each error."""
    name = type(exception).__name__
    message = str(exception.args[0]) if exception.args else ''
    description = message.splitlines()[0]

    traceback = message.splitlines()[1:]
    traceback = '\n' + '\n'.join(traceback)
    traceback = html.escape(traceback)

    message = Message(MessageRole.ASSISTANT, f'''
        <b class="m">{name}: {description}</b>
        <br>
        <pre class="code m">{traceback}</pre>
    ''')

    chat = Chat()  # Create a new chat instance for each error
    chat.show_message(message)
    chat.show_user_answers()  # Ensure input UI is tied to the correct chat

class MessageRole(Enum):
    USER = 'user'
    ASSISTANT = 'assistant'

class Buttons(Enum):
    EXPLAIN = 'Explain'
    GUIDE = 'What can I do?'
    MANUAL_PROMPT = 'Other'

class Message:
    def __init__(self, role: MessageRole, content: str):
        self.role = role
        icon_user = '''
            <div class="icon">
                <i class="fas fa-user"></i>
                <br>
                You 
            </div>
        '''
        icon_assistant = '''
            <div class="icon">
                <i class="fas fa-robot"></i>
                <br>
                AI 
            </div>
        '''
        no_icon = ''

        self.html = f'''
            <div class="messagebox messagebox-{role.value}">
                {icon_assistant if role == MessageRole.ASSISTANT else no_icon}    
                <div class="message">
                    {content}
                </div>
                {icon_user if role == MessageRole.USER else no_icon}
            </div>
        '''

class Chat:
    def __init__(self):
        global CHAT_ID
        CHAT_ID += 1
        self.chat_id = CHAT_ID

        self.output_widget = widgets.Output()  # Capture output in Jupyter cell

        self.html = f'''
            <style>{CSS}</style>
            <div class="box" id="chat{self.chat_id}">
            </div>
        '''

        self.display_html(self.html)
        display(self.output_widget)  # Ensure output appears inside the correct cell

    def display_html(self, content: str):
        with self.output_widget:
            display(HTML(content))

    def display_box(self, content: list[widgets.Widget]):
        with self.output_widget:
            display(widgets.HBox(content))

    def show_message(self, message: Message):
        message_html = message.html.replace('`', '\\`').replace('\\', '\\\\')

        append_script = f'''
            <script>
                var target = document.getElementById('chat{self.chat_id}');
                target.insertAdjacentHTML('beforeend', `{message_html}`);
                target.scrollTop = target.scrollHeight;
            </script>
        '''

        self.display_html(append_script)

    def show_user_answers(self):
        """Creates a set of buttons for the user to choose from."""
        options = [button.value for button in Buttons]
        buttons = [widgets.Button(description=option) for option in options]
        
        buttons[0].layout.margin = '2px 2px 2px 62px'
        for button in buttons[1:]:
            button.layout.margin = '2px 2px 2px 2px'

        def on_button_click(b):
            if b.description == Buttons.EXPLAIN.value:
                self.show_message(Message(MessageRole.USER, b.description))
            elif b.description == Buttons.GUIDE.value:
                self.show_message(Message(MessageRole.USER, b.description))
            elif b.description == Buttons.MANUAL_PROMPT.value:
                self.show_user_input()
            
            for button in buttons:
                button.close()

        # Assign on_click event to each button
        for button in buttons:
            button.on_click(on_button_click)

        self.display_box(buttons)

    def show_user_input(self):
        """Creates an interactive text input field with a send button."""
        self.text_input = widgets.Text(placeholder='Type here...', layout=widgets.Layout(width='100%'))
        self.send_button = widgets.Button(description='Send')
        self.back_button = widgets.Button(description='Back')

        self.text_input.on_submit(self.process_user_input)
        self.send_button.on_click(self.process_user_input)

        def show_user_answers(b):
            self.text_input.close()
            self.send_button.close()
            self.back_button.close()
            self.show_user_answers()
        self.back_button.on_click(show_user_answers)

        self.display_box([self.text_input, self.send_button, self.back_button])

    def process_user_input(self, b):
        """Handles user input and adds it to the chat UI."""
        user_text = self.text_input.value.strip()
        if user_text:
            self.show_message(Message(MessageRole.USER, user_text))
            self.text_input.close()
            self.send_button.close()
            self.back_button.close()
