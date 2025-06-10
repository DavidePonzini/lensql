from dav_tools import database
from .connection import db, SCHEMA

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

def remove_student(teacher: str, student: str) -> None:
    '''Remove a student from the teacher's list of students'''

    query = database.sql.SQL(
    '''
        DELETE FROM {schema}.teaches
        WHERE teacher = {teacher} AND student = {student}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        teacher=database.sql.Placeholder('teacher'),
        student=database.sql.Placeholder('student')
    )

    db.execute(query, {
        'teacher': teacher,
        'student': student
    })

def get_students(teacher: str) -> list[str]:
    '''Get all students of a teacher'''

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
        'username': teacher
    })

    return [{
        'id': row[0],
        'username': row[1]
    } for row in result]

def get_students_status(teacher: str) -> list[dict]:
    '''List student status for a given teacher'''

    query = database.sql.SQL('''
        SELECT
            username,
            (t.student IS NOT NULL) AS is_student
        FROM
            {schema}.users AS u
        LEFT JOIN
            {schema}.teaches AS t ON u.username = t.student AND t.teacher = {teacher}
        WHERE
            u.is_disabled = FALSE
        ORDER BY
            u.username
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        teacher=database.sql.Placeholder('teacher')
    )

    result = db.execute_and_fetch(query, {'teacher': teacher})

    return [
        {
            'username': row[0],
            'is_student': row[1],
        }
        for row in result
    ]
