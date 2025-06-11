from ...connection import get_connection as _get_connection
from ._queries import Queries as _Queries
from server.sql import SQLException, QueryResult, QueryResultDataset, QueryResultError
import pandas as pd

from dav_tools import messages


def _execute_builtin(username: str, query: _Queries) -> QueryResult:
    '''Runs a builtin query and returns the result.'''

    try:
        conn = _get_connection(username)
        with conn.cursor() as cur:
            cur.execute(query.value)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = pd.DataFrame(rows, columns=columns)


        conn.update_last_operation_ts()
        return QueryResultDataset(
            result=result,
            query=query.name,
            query_type='BUILTIN',
            notices=conn.notices)
    except Exception as e:
        try:
            conn.rollback()
            conn.update_last_operation_ts()
        except Exception as e:
            messages.error(f"Error rolling back connection for user {username}: {e}")
        return QueryResultError(
            exception=SQLException(e),
            query=query.name,
            query_type='BUILTIN',
            notices=conn.notices)

def list_schemas(username: str) -> QueryResult:
    '''Lists all schemas in the database.'''

    return _execute_builtin(username, _Queries.LIST_SCHEMAS)

def list_tables(username: str) -> QueryResult:
    '''Lists tables in the current search_path.'''

    return _execute_builtin(username, _Queries.LIST_TABLES)

def list_all_tables(username: str) -> QueryResult:
    '''Lists all tables in the database.'''

    return _execute_builtin(username, _Queries.LIST_ALL_TABLES)

def list_constraints(username: str) -> QueryResult:
    '''Lists all constraints in the database.'''

    return _execute_builtin(username, _Queries.LIST_CONSTRAINTS)

def show_search_path(username: str) -> QueryResult:
    '''Shows the search path for the database.'''

    return _execute_builtin(username, _Queries.SHOW_SEARCH_PATH)

def view_expected_result(username: str, exercise_id: int) -> QueryResult:
    '''Views the expected result for a given exercise.'''

    # TODO
    return _execute_builtin(username, _Queries.VIEW_EXPECTED_RESULT(exercise_id))