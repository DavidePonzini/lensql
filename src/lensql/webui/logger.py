from typing import Any
from .. import database

def log_button(button: str, query: str, data: str, chat_id: int, msg_id: int):
    db = database.logger_connect()
    db.insert('lensql_log', 'buttons', {
        'username': database.USERNAME,
        'button': button,
        'query': query,
        'data': data,
        'chat_id': chat_id,
        'msg_id': msg_id,
    })

def log_query(query: str, success: bool):
    db = database.logger_connect()
    db.insert('lensql_log', 'queries', {
        'username': database.USERNAME,
        'query': query,
        'success': success,
    })

