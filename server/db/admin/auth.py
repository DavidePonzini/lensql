from dav_tools import database
from .connection import db, SCHEMA

import bcrypt

def _hash_password(password: str) -> str:
    '''Hash a password using bcrypt'''
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

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

def register_user(username: str, password: str, *, school: str, email: str, is_admin: bool = False) -> bool:
    '''Register a new user'''

    if user_exists(username):
        return False

    hashed_password = _hash_password(password)

    query = database.sql.SQL('''
        INSERT INTO {schema}.users(username, password_hash, email, school, is_admin)
        VALUES ({username}, {password_hash}, {email}, {school}, {is_admin})
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        password_hash=database.sql.Placeholder('password_hash'),
        email=database.sql.Placeholder('email'),
        school=database.sql.Placeholder('school'),
        is_admin=database.sql.Placeholder('is_admin')
    )

    db.execute(query, {
        'username': username,
        'password_hash': hashed_password,
        'email': email,
        'school': school,
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

    db.execute(query, {
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


def change_password(username: str, new_password: str) -> bool:
    '''Change the password for a user'''

    if not user_exists(username):
        return False

    hashed_new_password = _hash_password(new_password)

    query = database.sql.SQL('''
        UPDATE {schema}.users
        SET password_hash = {new_password}
        WHERE username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        new_password=database.sql.Placeholder('new_password'),
        username=database.sql.Placeholder('username')
    )

    db.execute(query, {
        'new_password': hashed_new_password,
        'username': username
    })

    return True