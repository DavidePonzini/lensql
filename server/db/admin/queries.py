import json
from dav_tools import database
import pandas as pd
from .connection import db, SCHEMA

def log_batch(username: str, exercise_id: int) -> int:
    '''Log a new query batch for a user and exercise ID.'''

    result = db.insert(SCHEMA, 'query_batches', {
        'username': username,
        'exercise_id': exercise_id,
    }, ['id'])

    batch_id = result[0][0]
    return batch_id

def log(*,
        username: str,
        batch_id: int,
        query: str,
        search_path: str | None = None,
        success: bool,
        result: str,
        query_type: str,
        query_goal: str) -> int:
    '''Log a new query with its result and success status.'''

    result = db.insert(SCHEMA, 'queries', {
        'batch_id': batch_id,
        'query': query,
        'search_path': search_path,
        'success': success,
        'result': result,
        'query_type': query_type,
        'query_goal': query_goal,
    }, ['id'])

    query_id = result[0][0]

    # Log in unique queries table
    if query_type != 'BUILTIN':
        statement = database.sql.SQL(
            '''
            INSERT INTO {schema}.user_unique_queries (username, query_hash)
            VALUES ({username}, MD5({query}))
            ON CONFLICT (username, query_hash) DO NOTHING
            '''
        ).format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            query=database.sql.Placeholder('query')
        )
        db.execute(statement, {
            'username': username,
            'query': query
        })

    return query_id

def is_new_query(username: str, query: str) -> bool:
    '''Check if a query is new for the user.'''

    statement = database.sql.SQL('''
        SELECT COUNT(*)
        FROM {schema}.user_unique_queries
        WHERE username = {username}
        AND query_hash = MD5({query})
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        query=database.sql.Placeholder('query')
    )

    result = db.execute_and_fetch(statement, {
        'username': username,
        'query': query
    })

    return result[0][0] == 0

def log_context(query_id: int, columns: list[dict], unique_columns: list[dict]) -> None:
    '''Log context for a query.'''

    for column in columns:
        db.insert(SCHEMA, 'query_context_columns', {
            'query_id': query_id,
            'schema_name': column['schema_name'],
            'table_name': column['table_name'],
            'column_name': column['column_name'],
            'column_type': column['column_type'],
            'numeric_precision': column['numeric_precision'],
            'numeric_scale': column['numeric_scale'],
            'is_nullable': column['is_nullable'],
            'foreign_key_schema': column['foreign_key_schema'],
            'foreign_key_table': column['foreign_key_table'],
            'foreign_key_column': column['foreign_key_column'],
        })

    for column in unique_columns:
        db.insert(SCHEMA, 'query_context_columns_unique', {
            'query_id': query_id,
            'schema_name': column['schema_name'],
            'table_name': column['table_name'],
            'constraint_type': column['constraint_type'],
            'columns': column['columns'],
        })

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
