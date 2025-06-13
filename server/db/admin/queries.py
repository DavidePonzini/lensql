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

def log(batch_id: int, query: str, *,
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

    return query_id

def log_context(query_id: int, columns: list[dict], unique_columns: list[dict]) -> None:
    '''Log context for a query.'''

    for column in columns:
        db.insert(SCHEMA, 'query_context_columns', {
            'query_id': query_id,
            'schema_name': column['schema_name'],
            'table_name': column['table_name'],
            'column_name': column['column_name'],
            'column_type': column['column_type'],
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
