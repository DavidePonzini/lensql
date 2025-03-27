from . import load_content
from ..sql_errors import SQLException

from dav_tools.chatgpt import MessageRole

import html

CSS = load_content.load_from_this_dir('style.css')


class HtmlComponent:
    def __init__(self, html: str):
        self.html = html

    def __str__(self):
        return self.html


class Icon:
    USER = '''
        <div class="icon">
            <i class="fas fa-user"></i>
            <br>
            You 
        </div>
    '''
    ASSISTANT = '''
        <div class="icon">
            <i class="fas fa-search"></i>
            <br>
            LensQL
        </div>
    '''
    NO_ICON = ''

def exception_to_html(exception: SQLException) -> str:
    traceback = '\n' + '\n'.join(exception.traceback)
    traceback = html.escape(traceback)

    return f'''
        <b class="m">{exception}</b>
        <br>
        <pre class="code m">{traceback}</pre>
    '''

class Chat(HtmlComponent):
    def __init__(self, id: int):
        super().__init__(f'''
                <style>{CSS}</style>
            
                <div class="box" id="chat{id}"></div>
            ''')

class Message(HtmlComponent):
    def __init__(self, role: MessageRole, content: str, msg_id: int):
        super().__init__(f'''
                <div class="messagebox messagebox-{role}" id="msg{msg_id}">
                    {Icon.ASSISTANT if role == MessageRole.ASSISTANT else Icon.NO_ICON}    
                    <div class="message">
                        {content}
                    </div>
                    {Icon.USER if role == MessageRole.USER else Icon.NO_ICON}
                </div>
            ''')
