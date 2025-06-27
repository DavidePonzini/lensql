from pydantic import BaseModel

class MessageFormat(BaseModel):
    introduction: str
    response: str
    motivational_message: str

def format_response(message: MessageFormat) -> str:
    '''
    Format the response from the LLM into a string.
    '''

    introduction = text_to_html(message.introduction)
    response = text_to_html(message.response, replace_newlines=False)
    motivational_message = text_to_html(message.motivational_message)

    return f'''
        <div>{introduction}</div>
        <br>
        <div>{response}</div>
        <br>
        <i>{motivational_message}</i>
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