from ._queries import Queries as _Queries
from ...connection import get_connection as _get_connection

import pandas as pd


def _execute(username: str, query: _Queries) -> list[tuple]:
    '''Runs a builtin query and returns the result.'''

    conn = _get_connection(username)
    with conn.cursor() as cur:
        cur.execute(query.value)

        conn.update_last_operation_ts()

        return cur.fetchall()

def get_search_path(username: str) -> str:
    '''Returns the current search path for the user.'''

    result = _execute(username, _Queries.SEARCH_PATH)

    return result[0][0]

def get_columns(username: str) -> list[dict]:
    '''Lists all tables'''

    result = _execute(username, _Queries.COLUMNS)

    return [
        {
            'schema_name': row[0],
            'table_name': row[1],
            'column_name': row[2],
            'column_type': row[3],
            'numeric_precision': row[4],
            'numeric_scale': row[5],
            'is_nullable': row[6],
            'foreign_key_schema': row[7],
            'foreign_key_table': row[8],
            'foreign_key_column': row[9],
        }
        for row in result
    ]

def get_unique_columns(username: str) -> list[dict]:
    '''Lists unique columns.'''

    result = _execute(username, _Queries.UNIQUE_COLUMNS)

    return [
        {
            'schema_name': row[0],
            'table_name': row[1],
            'constraint_type': row[2],
            'columns': row[3]
        }
        for row in result
    ]