from . import database

def log_button(button: str, query: str, success: bool, data: str, chat_id: int, msg_id: int):
    if database.SKIP_LOGGING:
        return

    db = database.logger_connect()
    db.insert('lensql_log', 'buttons', {
        'username': database.USERNAME,
        'button': button,
        'query': query,
        'success': success,
        'data': data,
        'chat_id': chat_id,
        'msg_id': msg_id,
    })

def log_query(query: str, success: bool):
    if database.SKIP_LOGGING:
        return
    
    db = database.logger_connect()
    db.insert('lensql_log', 'queries', {
        'username': database.USERNAME,
        'query': query,
        'success': success,
    })

