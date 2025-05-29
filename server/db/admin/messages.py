from dav_tools import database
from .connection import db, SCHEMA

def log(answer: str, button: str, query_id: str, msg_idx: int) -> int:
    '''Log a new message'''

    result = db.insert(SCHEMA, 'messages', {
        'query_id': query_id,
        'answer': answer,
        'button': button,
        'msg_idx': msg_idx,
    }, ['id'])

    message_id = result[0][0]

    return message_id

def log_feedback(message_id: int, feedback: bool, username: str) -> None:
    '''Log feedback for a message'''

    query = database.sql.SQL(
    '''
        UPDATE {schema}.messages AS m
        SET
            feedback = {feedback},
            feedback_ts = NOW()
        FROM {schema}.queries AS q
        JOIN {schema}.query_batches AS qb ON q.batch_id = qb.id
        WHERE m.id = {message_id}
        AND m.query_id = q.id
        AND qb.username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        feedback=database.sql.Placeholder('feedback'),
        message_id=database.sql.Placeholder('message_id'),
        username=database.sql.Placeholder('username')
    )

    db.execute(query, {
        'feedback': feedback,
        'message_id': message_id,
        'username': username
    })
