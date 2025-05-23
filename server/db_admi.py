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
    '''Get all assignments assigned to a user'''

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
            a.deadline_ts,
            e.title,
            e.id
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

def get_all_exercises() -> list[dict]:
    '''Get all exercises in the database'''

    query = database.sql.SQL(
    '''
        SELECT
            e.id,
            e.title,
            e.request,
            e.dataset_id,
            d.name,
            e.expected_answer,
            e.is_ai_generated
        FROM
            {schema}.exercises e
            LEFT JOIN {schema}.datasets d ON e.dataset_id = d.id
        ORDER BY
            e.title,
            e.id
    ''').format(
        schema=database.sql.Identifier(SCHEMA)
    )

    result = db.execute_and_fetch(query)

    return [
        {
            'id': row[0],
            'title': row[1],
            'request': row[2],
            'dataset_id': row[3],
            'dataset_name': row[4] if row[3] else 'None',
            'expected_answer': row[5],
            'is_ai_generated': row[6]
        }
        for row in result
    ]


def get_exercise(exercise_id: int, username: str) -> dict:
    '''Get the exercise for a given ID, if the user is assigned to it'''

    query = database.sql.SQL(
    '''
        SELECT
            e.request,
            e.dataset_id
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
        'dataset_id': result[0][1]
    }

def get_exercise_dataset(exercise_id: int) -> str:
    '''Get the dataset for a given exercise ID'''

    query = database.sql.SQL(
        '''
        SELECT dataset
        FROM {schema}.exercises e
            JOIN {schema}.datasets d ON e.dataset_id = d.id                     
        WHERE e.id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id
    })

    if len(result) == 0:
        return '-- No dataset provided'

    return result[0][0]

def get_dataset(dataset_id: int | None) -> str:
    '''Get the dataset for a given dataset ID'''

    if dataset_id is None:
        return '-- No dataset provided'

    query = database.sql.SQL(
        '''
        SELECT dataset
        FROM {schema}.datasets
        WHERE id = {dataset_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        dataset_id=database.sql.Placeholder('dataset_id')
    )

    result = db.execute_and_fetch(query, {
        'dataset_id': dataset_id
    })

    if len(result) == 0:
        return '-- No dataset provided'

    return result[0][0]

def add_student(teacher: str, student: str) -> None:
    '''Add a student to the teacher's list of students'''

    query = database.sql.SQL(
    '''
        INSERT INTO {schema}.teaches(teacher, student)
        VALUES ({teacher}, {student})
        ON CONFLICT (teacher, student) DO NOTHING
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        teacher=database.sql.Placeholder('teacher'),
        student=database.sql.Placeholder('student')
    )

    db.execute(query, {
        'teacher': teacher,
        'student': student
    })

def get_datasets(username: str) -> list[dict]:
    '''Get all datasets visible to the user'''

    query = database.sql.SQL(
    '''
        SELECT
            d.id,
            d.name
        FROM
            {schema}.datasets d
            JOIN {schema}.has_dataset hd ON d.id = hd.dataset_id
        WHERE
            hd.username = {username}
        ORDER BY
            d.name
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
            'name': row[1]
        }
        for row in result
    ]

def add_dataset(name: str, dataset: str) -> None:
    '''Add a dataset to the database'''

    query = database.sql.SQL(
    '''
        INSERT INTO {schema}.datasets(name, dataset)
        VALUES ({name}, {dataset})
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        name=database.sql.Placeholder('name'),
        dataset=database.sql.Placeholder('dataset')
    )

    db.execute(query, {
        'name': name,
        'dataset': dataset
    })

def get_assignment_students(username: str, exercise_id: int) -> dict:
    '''Get whether each student is assigned to the exercise'''

    query = database.sql.SQL(
    '''
        SELECT
            t.student AS student,
            (a.exercise_id IS NOT NULL) AS is_assigned
        FROM
            {schema}.teaches t
        LEFT JOIN
            {schema}.assignments a ON a.username = t.student AND a.exercise_id = {exercise_id}
        WHERE
            t.teacher = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id'),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id,
        'username': username
    })

    return [{
        'username': row[0],
        'is_assigned': row[1]
    } for row in result]

def get_students(username: str) -> list[str]:
    query = database.sql.SQL(
    '''
        SELECT
            t.student,
            u.username
        FROM
            {schema}.teaches t
            JOIN {schema}.users u ON t.student = u.username
        WHERE
            teacher = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return [{
        'id': row[0],
        'username': row[1]
    } for row in result]

def get_user_info(username: str) -> dict:
    query = database.sql.SQL(
    '''
        SELECT
            is_admin,
            is_teacher
        FROM
            {schema}.v_user_info
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
        return None
    return {
        'username': username,
        'is_admin': result[0][0],
        'is_teacher': result[0][1],
    }

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

def add_exercise(title: str, request: str, dataset_id: int | None, expected_answer: str):
    db.insert(SCHEMA, 'exercises', {
        'title': title,
        'request': request,
        'dataset_id': dataset_id,
        'expected_answer': expected_answer,
        'is_ai_generated': False
    })

def edit_exercise(exercise_id: int, title: str, request: str, dataset_id: int | None, expected_answer: str) -> None:
    query = database.sql.SQL('''
        UPDATE {schema}.exercises
        SET title = {title},
            request = {request},
            dataset_id = {dataset_id},
            expected_answer = {expected_answer}
        WHERE id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        title=database.sql.Placeholder('title'),
        request=database.sql.Placeholder('request'),
        dataset_id=database.sql.Placeholder('dataset_id'),
        expected_answer=database.sql.Placeholder('expected_answer'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )
    db.execute(query, {
        'title': title,
        'request': request,
        'dataset_id': dataset_id,
        'expected_answer': expected_answer,
        'exercise_id': exercise_id
    })

def delete_exercise(exercise_id: int) -> None:
    try:
        query = database.sql.SQL('''
            DELETE FROM {schema}.exercises
            WHERE id = {exercise_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id')
        )
        db.execute(query, {
            'exercise_id': exercise_id
        })
    except Exception as e:
        return 

def assign_exercise(teacher: str, exercise_id: int, student: str) -> None:
    # Check if already assigned, skip if exists (optional safeguard)
    query_check = database.sql.SQL('''
        SELECT 1 FROM {schema}.assignments
        WHERE username = {student} AND exercise_id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        student=database.sql.Placeholder('student'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )
    exists = db.execute_and_fetch(query_check, {
        'student': student,
        'exercise_id': exercise_id
    })
    if exists:
        return

    db.insert(SCHEMA, 'assignments', {
        'username': student,
        'exercise_id': exercise_id
    })

def unassign_exercise(exercise_id: int, student: str) -> None:
    query = database.sql.SQL('''
        DELETE FROM {schema}.assignments
        WHERE username = {student}
        AND exercise_id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        student=database.sql.Placeholder('student'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )
    db.execute(query, {
        'student': student,
        'exercise_id': exercise_id
    })
