from dav_tools import database
from .connection import db, SCHEMA

import bcrypt

def register_user(username: str, password: str) -> None:
    '''Register a new user'''

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
    '''Check if a user can log in with the given credentials'''

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
