from typing import Literal

from dav_tools import database
import os

schema = 'lensql'

db = database.PostgreSQL(
    host =      os.getenv('LENSQL_HOST'),
    port =  int(os.getenv('LENSQL_PORT')),
    database =  os.getenv('LENSQL_DATABASE'),
    user =      os.getenv('LENSQL_USER'),
    password =  os.getenv('LENSQL_PASSWORD')
)

def can_login(username: str) -> bool:
    query = database.sql.SQL('''
                             SELECT 1
                             FROM
                                {schema}.users
                             WHERE
                                username = {username}
                                AND enabled
                             ''').format(
                                 schema=database.sql.Identifier(schema),
                                 username=database.sql.Placeholder('username')
                             )
    
    result = db.execute_and_fetch(query, {
        'username': username
    })

    return len(result) == 1    

def log_button(username: str, button: str, query: str, success: bool, data: str, chat_id: int, msg_id: int):
    db.insert(schema, 'buttons', {
        'username': username,
        'button': button,
        'query': query,
        'success': success,
        'data': data,
        'chat_id': chat_id,
        'msg_id': msg_id,
    })

def log_query(username: str, query: str, success: bool):
    db.insert(schema, 'queries', {
        'username': username,
        'query': query,
        'success': success,
    })

