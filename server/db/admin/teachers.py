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

