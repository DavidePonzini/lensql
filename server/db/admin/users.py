from dav_tools import database
from .connection import db, SCHEMA

def get_info(username: str) -> dict:
    '''Get general information about a user'''

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

def get_learning_stats(username: str) -> dict:
    '''Get learning statistics for a user'''

    statement = database.sql.SQL(
    '''
        SELECT
            query_type,
            queries,
            queries_d,
            queries_success
        FROM
            {schema}.v_query_types_per_user
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    result = db.execute_and_fetch(statement, {
        'username': username
    })

    return {
        'queries': sum(row[1] for row in result),
        'queries_d': sum(row[2] for row in result),
        'queries_success': sum(row[3] for row in result),
        'query_types': [
            {
                'type': row[0],
                'count': row[1],
                'count_d': row[2],
                'success': row[3]
            } for row in result
        ]
    }