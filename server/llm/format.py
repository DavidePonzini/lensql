from pydantic import BaseModel

class MessageFormat(BaseModel):
    introduction: str
    response: str
    motivational_message: str

    def __str__(self) -> str:
        introduction = text_to_html(self.introduction)
        response = text_to_html(self.response, replace_newlines=False)
        motivational_message = text_to_html(self.motivational_message)

        return f'''
            <div>{introduction}</div>
            <br>
            <div>{response}</div>
            <br>
            <i>{motivational_message}</i>
        '''
        

class MessageFormatWithCode(MessageFormat):
    code: str

    def __str__(self) -> str:
        introduction = text_to_html(self.introduction)
        response = text_to_html(self.response, replace_newlines=False)
        motivational_message = text_to_html(self.motivational_message)
        
        code = text_to_html(self.code, replace_newlines=False)
        if code.startswith('<pre class="code m">'):
            code = code[20:-6]  # Remove the <pre class="code m"> and </pre> tags

        return f'''
            <div>{introduction}</div>
            <br>
            <div>{response}</div>
            <pre class="code m">{code}</pre>
            <br>
            <i>{motivational_message}</i>
            <br>
        '''

def text_to_html(text: str, *, replace_newlines: bool = True) -> str:
    '''
    Convert plain text to HTML, replacing newlines with <br> tags.
    Also removes leading and trailing <br> tags.
    '''

    if replace_newlines:
        text = text.replace('\n', '<br>')

    while text.endswith('<br>'):
        text = text[:-4]
    while text.startswith('<br>'):
        text = text[4:]

    return text