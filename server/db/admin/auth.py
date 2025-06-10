from dav_tools import database
from .connection import db, SCHEMA

import bcrypt

def user_exists(username: str) -> bool:
    '''Check if a user exists in the database'''

    query = database.sql.SQL('''
        SELECT 1
        FROM {schema}.users
        WHERE username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    
    result = db.execute_and_fetch(query, {
        'username': username
    })

    return len(result) > 0

def register_user(username: str, password: str, *, is_teacher: bool = False, is_admin: bool = False) -> bool:
    '''Register a new user'''

    if user_exists(username):
        return False

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    query = database.sql.SQL('''
        INSERT INTO {schema}.users(username, password_hash, is_teacher, is_admin)
        VALUES ({username}, {password_hash}, {is_teacher}, {is_admin})
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        password_hash=database.sql.Placeholder('password_hash'),
        is_teacher=database.sql.Placeholder('is_teacher'),
        is_admin=database.sql.Placeholder('is_admin')
    )

    db.execute(query, {
        'username': username,
        'password_hash': hashed_password,
        'is_teacher': is_teacher,
        'is_admin': is_admin,
    })
    
    return True

def delete_user(username: str) -> None:
    '''Delete a user'''

    query = database.sql.SQL('''
        DELETE FROM {schema}.users
        WHERE username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute(query, {
        'username': username
    })

def can_login(username: str, password: str) -> bool:
    '''Check if a user can log in with the given credentials'''

    query = database.sql.SQL('''
        SELECT password_hash
        FROM
            {schema}.users
        WHERE
            username = {username}
            AND NOT is_disabled
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

