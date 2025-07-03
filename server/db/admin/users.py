from dav_tools import database
from .connection import db, SCHEMA

def is_admin(username: str) -> bool:
    '''Check if a user is an admin'''

    query = database.sql.SQL('''
        SELECT
            is_admin
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

def get_info(username: str) -> dict:
    '''Get general information about a user'''

    return {
        'username': username,
        'is_admin': is_admin(username),
    }

def get_unique_queries_count(username: str) -> int:
    '''Get the amount of unique queries run by the user'''

    query = database.sql.SQL('''
        SELECT
            COUNT(DISTINCT q.query)
        FROM
            {schema}.queries q
            JOIN {schema}.query_batches qb ON qb.id = q.batch_id
        WHERE
            qb.username = {username}
            AND q.query_type <> 'BUILTIN'
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return result[0][0]

def get_query_stats(username: str) -> dict:
    '''Get, for each query type, the amount of queries run by the user'''

    query = database.sql.SQL('''
    SELECT
        q.query_type,
        COUNT(q.id) AS queries,
        COUNT(DISTINCT q.query) AS queries_d,
        SUM(CASE WHEN q.success THEN 1 ELSE 0 END) AS queries_success
    FROM
        {schema}.queries q
        JOIN {schema}.query_batches qb ON qb.id = q.batch_id
    WHERE
        qb.username = {username}
        AND q.query_type <> 'BUILTIN'
    GROUP BY
        q.query_type
    ORDER BY
        queries DESC;
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    result = db.execute_and_fetch(query, {
        'username': username
    })

    return {
        'queries': sum(row[1] for row in result),
        'queries_d': sum(row[2] for row in result),
        'queries_success': sum(row[3] for row in result),
        'queries_select': sum(row[1] for row in result if row[0] == 'SELECT'),
        'queries_success_select': sum(row[3] for row in result if row[0] == 'SELECT'),
        'query_types': [
            {
                'type': row[0],
                'count': row[1],
                'count_d': row[2],
                'success': row[3]
            } for row in result
        ],
    }

def get_message_stats(username: str) -> dict:
    '''Get statistics about chat interactions for a user'''

    query = database.sql.SQL(
    '''
    SELECT
        COUNT(button) AS count,
        SUM(CASE WHEN query_type = 'SELECT' THEN 1 ELSE 0 END) AS select_count,
        SUM(CASE WHEN success THEN 1 ELSE 0 END) AS success_count,
        SUM(CASE WHEN feedback IS NOT NULL THEN 1 ELSE 0 END) AS feedback_count
    FROM
        {schema}.messages m
        JOIN {schema}.queries q ON q.id = m.query_id
        JOIN {schema}.query_batches qb ON qb.id = q.batch_id
    WHERE
        qb.username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )
    result = db.execute_and_fetch(query, {
        'username': username
    })[0]

    return {
        'messages': result[0],
        'messages_select': result[1],
        'messages_success': result[2],
        'messages_feedback': result[3],
    }

def get_error_stats(username: str) -> dict:
    '''Get statistics about errors for a user'''

    # TODO
    return {}
