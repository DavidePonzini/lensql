from dav_tools import database
import os
import bcrypt

SCHEMA = 'lensql'

db = database.PostgreSQL(
    host        =       os.getenv('DB_HOST'),
    port        =   int(os.getenv('DB_PORT')),
    database    =       os.getenv('DB_DATABASE'),
    user        =       os.getenv('DB_USERNAME'),
    password    =       os.getenv('DB_PASSWORD')
)

def register_user(username: str, password: str) -> None:
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    query = database.sql.SQL('''
        INSERT INTO {schema}.users(username, password_hash)
        VALUES ({username}, {password_hash})
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        password_hash=database.sql.Placeholder('password_hash')
    )

    db.execute(query, {
        'username': username,
        'password_hash': hashed_password
    })

def can_login(username: str, password: str) -> bool:
    query = database.sql.SQL('''
        SELECT password_hash
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

    if not result:
        return False
    
    stored_hash = result[0][0]
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def log_message(answer: str, button: str, query_id: str, msg_idx: int) -> int:
    result = db.insert(SCHEMA, 'messages', {
        'query_id': query_id,
        'answer': answer,
        'button': button,
        'msg_idx': msg_idx,
    }, ['id'])

    message_id = result[0][0]

    return message_id

def log_query_batch(username: str, exercise_id: int) -> int:
    result = db.insert(SCHEMA, 'query_batches', {
        'username': username,
        'exercise_id': exercise_id,
    }, ['id'])

    batch_id = result[0][0]
    return batch_id

def log_query(batch_id: int, query: str, success: bool, result_str: str) -> int:
    result = db.insert(SCHEMA, 'queries', {
        'batch_id': batch_id,
        'query': query,
        'success': success,
        'result': result_str
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

def get_query_result(query_id: int) -> str:
    query = database.sql.SQL('''
        SELECT result
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

def log_feedback(message_id: int, feedback: bool, username: str) -> None:
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

def get_assignments(username: str) -> list:
    query = database.sql.SQL(
    '''
        SELECT
            e.id,
            e.title,
            e.request,
            a.deadline_ts,
            a.submission_ts,
            e.is_ai_generated
        FROM
            {schema}.assignments a
            JOIN {schema}.exercises e ON a.exercise_id = e.id
        WHERE
            username = {username}
        ORDER BY
            CASE WHEN a.submission_ts IS NULL THEN 0 ELSE 1 END,
            a.deadline_ts
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return [
        {
            'id': row[0],
            'title': row[1],
            'request': row[2],
            'deadline_ts': row[3],
            'submission_ts': row[4],
            'is_ai_generated': row[5]
        }
        for row in result
    ]

def get_exercise(exercise_id: int, username: str) -> dict:
    query = database.sql.SQL(
    '''
        SELECT
            e.request,
            e.dataset
        FROM
            {schema}.exercises e
            JOIN {schema}.assignments a ON e.id = a.exercise_id
        WHERE
            e.id = {exercise_id}
            AND a.username = {username} 
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id'),
        username=database.sql.Placeholder('username'),
    )
    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id,
        'username': username,
    })
    if len(result) == 0:
        return None
    return {
        'request': result[0][0],
    }

def get_exercise_dataset(exercise_id: int) -> str:
    query = database.sql.SQL('''
        SELECT dataset
        FROM {schema}.exercises
        WHERE id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id
    })

    if len(result) == 0:
        return None

    return result[0][0]

def get_students(username: str) -> list[str]:
    query = database.sql.SQL(
    '''
        SELECT
            student
        FROM
            {schema}.teaches
        WHERE
            teacher = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return [row[0] for row in result]

def is_teacher(username: str) -> bool:
    query = database.sql.SQL(
    '''
        SELECT 1
        FROM
            {schema}.teaches
        WHERE
            teacher = {username}
        LIMIT 1
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return len(result) > 0

def is_admin(username: str) -> bool:
    query = database.sql.SQL(
    '''
        SELECT is_admin
        FROM
            {schema}.users
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    if len(result) == 0:
        return False
    return result[0][0]

def create_exercise(title: str, request: str, dataset: str, expected_answer: str, is_ai_generated: bool) -> int:
    result = db.insert(SCHEMA, 'exercises', {
        'title': title,
        'request': request,
        'dataset': dataset,
        'expected_answer': expected_answer,
        'is_ai_generated': is_ai_generated
    }, ['id'])

    exercise_id = result[0][0]

    return exercise_id

def assign_exercise(username: str, exercise_id: int, deadline_ts: str) -> None:
    db.insert(SCHEMA, 'assignments', {
        'username': username,
        'exercise_id': exercise_id,
        'deadline_ts': deadline_ts
    })

def submit_assignment(username: str, exercise_id: int) -> None:
    query = database.sql.SQL(
    '''
        UPDATE {schema}.assignments
        SET submission_ts = NOW()
        WHERE
            username = {username}
            AND exercise_id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    db.execute(query, {
        'username': username,
        'exercise_id': exercise_id
    })

def unsubmit_assignment(username: str, exercise_id: int) -> None:
    query = database.sql.SQL(
    '''
        UPDATE {schema}.assignments
        SET submission_ts = NULL
        WHERE
            username = {username}
            AND exercise_id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    db.execute(query, {
        'username': username,
        'exercise_id': exercise_id
    })