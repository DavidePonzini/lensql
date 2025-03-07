from enum import Enum
from IPython import get_ipython
from IPython.display import display, HTML
import utils
import html


CHAT_ID = 0
CSS = utils.load_file('style.css')


def show_result(result, shell = get_ipython()) -> None:
    display(result)

def show_error(exception: Exception, shell = get_ipython()) -> None:
    # shell.showtraceback((type(exception), exception, exception.__traceback__))
    
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
    
    message2 = Message(MessageRole.USER, f'''
            <p>Can you explain?</p>
        ''')
    
    chat = Chat()
    chat.add_message(message)
    chat.add_message(message2)

class MessageRole(Enum):
    USER = 'user'
    ASSISTANT = 'assistant'

class Message:
    def __init__(self, role: MessageRole, content: str):
        self.role = role
        icon_user = '''
            <div class="icon">
                <i class="fas fa-exclamation-triangle"></i>
                <br>
                You 
            </div>
        '''
        icon_assistant = '''
            <div class="icon">
                <i class="fas fa-exclamation-triangle"></i>
                <br>
                Insert AI name here 
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

        self.html = f'''
            <style>{CSS}</style>

            <div class="box" id="chat{CHAT_ID}">
                
            </div>
        '''

        display(HTML(self.html))

    def add_message(self, message: Message):
        message_html = message.html.replace('`', '\\`').replace('\\', '\\\\')

        append_script = f'''
            <script>
                var messagebox = document.getElementById('chat{CHAT_ID}');
                messagebox.innerHTML += `{message_html}`;
            </script>
        '''
        
        display(HTML(append_script))
