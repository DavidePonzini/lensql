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
        }).json()
        
        if response['status'] == 'ok':
            return True
        
        messages.error('Error connecting user to the server:', response['message'])
        return False
    except Exception as e:
        messages.error('Error connecting user to the server:', e)
        return False


def log_query(query: str, success: bool) -> int:
    response = requests.post(f'{HOST}/log-query', data={
        'username': json.dumps(USERNAME),
        'query': json.dumps(query),
        'success': json.dumps(success)
    }).json()

    return response['query_id']

def explain_error_message(query_id: int, exception: str, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/explain-error-message', data={
        'username': json.dumps(USERNAME),
        'query_id': json.dumps(query_id),
        'exception': json.dumps(exception),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    }).json()

    return response['answer']

def locate_error_cause(query_id: int, exception: str, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/locate-error-cause', data={
        'username': json.dumps(USERNAME),
        'query_id': json.dumps(query_id),
        'exception': json.dumps(exception),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    }).json()

    return response['answer']

def provide_error_example(query_id: int, exception:str, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/provide-error-example', data={
        'username': json.dumps(USERNAME),
        'query_id': json.dumps(query_id),
        'exception': json.dumps(exception),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    }).json()

    return response['answer']

def fix_query(query_id: int, expection: str, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/fix-query', data={
        'username': json.dumps(USERNAME),
        'query_id': json.dumps(query_id),
        'exception': json.dumps(expection),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    }).json()
    
    return response['answer']

def describe_my_query(query_id: int, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/describe-my-query', data={
        'username': json.dumps(USERNAME),
        'query_id': json.dumps(query_id),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    }).json()
    
    return response['answer']

def explain_my_query(query_id: int, chat_id: int, msg_id: int) -> str:
    response = requests.post(f'{HOST}/explain-my-query', data={
        'username': json.dumps(USERNAME),
        'query_id': json.dumps(query_id),
        'chat_id': json.dumps(chat_id),
        'msg_id': json.dumps(msg_id)
    }).json()
    
    return response['answer']
