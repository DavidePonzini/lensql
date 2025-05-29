from dav_tools import database
from .connection import db, SCHEMA

def log_batch(username: str, exercise_id: int) -> int:
    '''Log a new query batch for a user and exercise ID.'''

    result = db.insert(SCHEMA, 'query_batches', {
        'username': username,
        'exercise_id': exercise_id,
    }, ['id'])

    batch_id = result[0][0]
    return batch_id

def log(batch_id: int, query: str, success: bool, result_str: str, query_type: str) -> int:
    '''Log a new query with its result and success status.'''

    result = db.insert(SCHEMA, 'queries', {
        'batch_id': batch_id,
        'query': query,
        'success': success,
        'result': result_str,
        'query_type': query_type
    }, ['id'])

    query_id = result[0][0]

    return query_id

def get(query_id: int) -> str:
    '''Get the query string for a given query ID.'''

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

def get_result(query_id: int) -> str:
    '''Get the result string for a given query ID.'''

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
