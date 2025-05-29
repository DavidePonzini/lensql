from dav_tools import database
from .connection import db, SCHEMA


def list_all(username: str) -> list:
    '''Get all exercises assigned to a user'''

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

def submit(username: str, exercise_id: int) -> None:
    '''Submit an assignment'''

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

def unsubmit(username: str, exercise_id: int) -> None:
    '''Unsubmit an assignment'''

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

def get_students(teacher: str, exercise_id: int) -> dict:
    '''Get whether each student of this teacher is assigned to the given exercise'''

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
        'username': teacher
    })

    return [{
        'username': row[0],
        'is_assigned': row[1]
    } for row in result]
