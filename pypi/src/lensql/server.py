import requests
import json
from dav_tools import messages

HOST = None
USERNAME = None

def login(host: str, username: str) -> bool:
    '''Connects the user to the server.'''
    global HOST, USERNAME

    HOST = host
    USERNAME = username

    try:
        response = requests.post(f'{HOST}/login', data={
            'username': json.dumps(USERNAME)
        })
        
        if response.json()['status'] == 'ok':
            return True
        
        messages.error('Error connecting user to the server:', response.json())
        return False
    except Exception as e:
        messages.error('Error connecting user to the server:', e)
        return False


def log_query(query: str, success: bool) -> None:
    requests.post(f'{HOST}/log-query', data={
        'username': json.dumps(USERNAME),
        'query': json.dumps(query),
        'success': json.dumps(success)
    })

def explain_error_message(query: str, exception: str, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/explain-error-message', data={
        'username': json.dumps(USERNAME),
        'query': json.dumps(query),
        'exception': json.dumps(exception),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    })

    return response.text

def identify_error_cause(query: str, exception: str, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/identify-error-cause', data={
        'username': json.dumps(USERNAME),
        'query': json.dumps(query),
        'exception': json.dumps(exception),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    })

    return response.text

def explain_my_query(query: str, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/explain-my-query', data={
        'username': json.dumps(USERNAME),
        'query': json.dumps(query),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    })
    
    return response.text
