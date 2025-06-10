from dav_tools import database
from .connection import db, SCHEMA
from . import users

def set_admin(current_user: str, username: str, value: bool) -> None:
    '''Set a user as admin or not'''

    # Cannot give or remove admin rights to oneself
    if username == current_user:
        return False

    if not users.is_admin(current_user):
        return False

    query = database.sql.SQL('''
        UPDATE
            {schema}.users
        SET
            is_admin = {value}
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        value=database.sql.Placeholder('value'),
        username=database.sql.Placeholder('username')
    )
    db.execute(query, {
        'value': value,
        'username': username
    })

    return True

def set_teacher(current_user: str, username: str, value: bool) -> None:
    '''Set a user as teacher or not'''

    if not users.is_admin(current_user):
        return False

    query = database.sql.SQL('''
        UPDATE
            {schema}.users
        SET
            is_teacher = {value}
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        value=database.sql.Placeholder('value'),
        username=database.sql.Placeholder('username')
    )
    db.execute(query, {
        'value': value,
        'username': username
    })

    return True

def list_all_users(current_user: str) -> list[dict]:
    '''List all users in the database'''

    if not users.is_admin(current_user):
        return []

    query = database.sql.SQL('''
        SELECT
            username,
            is_admin,
            is_teacher
        FROM
            {schema}.users
        WHERE
            NOT is_disabled
        ORDER BY
            username
    ''').format(
        schema=database.sql.Identifier(SCHEMA)
    )

    result = db.execute_and_fetch(query)

    return [
        {
            'username': row[0],
            'is_admin': row[1],
            'is_teacher': row[2],
        }
        for row in result
    ]


