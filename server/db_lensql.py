from dav_tools import database
import os

SCHEMA = 'lensql'

db = database.PostgreSQL(
    host        =       os.getenv('DB_HOST'),
    port        =   int(os.getenv('DB_PORT')),
    database    =       os.getenv('DB_DATABASE'),
    user        =       os.getenv('DB_USERNAME'),
    password    =       os.getenv('DB_PASSWORD')
)

def can_login(username: str) -> bool:
    query = database.sql.SQL('''
        SELECT 1
        FROM
            {schema}.users
        WHERE
            username = {username}
            AND can_login
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return len(result) == 1    

def log_message(content: str, button: str, query_id: str, data: str, chat_id: int, msg_id: int) -> int:
    result = db.insert(SCHEMA, 'messages', {
        'query_id': query_id,
        'content': content,
        'button': button,
        'data': data,
        'chat_id': chat_id,
        'msg_id': msg_id,
    }, ['id'])

    message_id = result[0][0]

    return message_id

def log_query(username: str, query: str, success: bool) -> int:
    result = db.insert(SCHEMA, 'queries', {
        'username': username,
        'query': query,
        'success': success,
    }, ['id'])

    query_id = result[0][0]

    return query_id

def get_query(query_id: int) -> str:
    query = database.sql.SQL('''
        SELECT query
        FROM {schema}.queries
        WHERE id = {query_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        query_id=database.sql.Placeholder('query_id')
    )
    result = db.execute_and_fetch(query, {
        'query_id': query_id
    })

    if len(result) == 0:
        return None

    return result[0][0]

def log_feedback(message_id: int, feedback: str):
    query = database.sql.SQL('''
        UPDATE {schema}.messages
        SET feedback = {feedback}
        WHERE id = {message_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        feedback=database.sql.Placeholder('feedback'),
        message_id=database.sql.Placeholder('message_id')
    )

    db.execute(query, {
        'feedback': feedback,
        'message_id': message_id
    })

