import pandas as pd
from . import util
from server.sql import QueryResult, QueryResultDataset, QueryResultMessage, SQLCode, Column, get_datatype_name
from server.db.users.connection import get_connection
from dav_tools import messages

NAME = 'CHECK_SOLUTION'


def _execute(username: str, query: str) -> QueryResultDataset | None:
    statements = SQLCode(query).split()

    # Only execute the first statement
    statement = util.next_statement(statements)
    if statement is None:
        return None
    
    # Only SELECT queries are supported
    if statement.query_type != 'SELECT':
        return None
    try:
        conn = get_connection(username)
        
        with conn.cursor() as cur:
            cur.execute(statement.query)
            conn.update_last_operation_ts()

            # If the query doesn't have a result set, we don't need it   
            if not cur.description:
                return None

            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            return QueryResultDataset(
                result=pd.DataFrame(rows, columns=columns),
                columns=[Column(name=col.name, data_type=col.type_code) for col in cur.description] if cur.description else [],
                query=statement.query,
                query_type='SELECT',
                query_goal='',
                notices=conn.notices)

    except Exception as e:
        try:
            conn.rollback()
            conn.update_last_operation_ts()
        except Exception as e:
            messages.error(f"Error rolling back connection for user {username}: {e}")
        return None



def check(username: str, query_user: str, query_solution: str) -> QueryResult:
    '''
    Checks the user's solution against the exercise solution.
    If multiple queries are present, only the first one is checked.
    If the exercise has no solution, a message is returned.
    Args:
        username (str): The username of the user.
        query_user (str): The SQL query submitted by the user.
        solution (str): The SQL solution for the exercise.

    Returns:
        QueryResult: The result of the comparison between the user's query and the exercise solution.
        If the exercise has no solution, a message indicating that is returned.
    '''

    if not query_solution:
        return QueryResultMessage(
            message=f'No solution found for this exercise.',
            query=NAME,
            query_type='BUILTIN',
            query_goal='BUILTIN',
            notices=[])
    
    result_user = _execute(username, query_user)
    if result_user is None:
        return QueryResultMessage(
            message=f'<i class="fa fa-exclamation-triangle text-danger me-1"></i>User query is not supported. Please ensure it is a valid SQL SELECT query.',
            query=NAME,
            query_type='BUILTIN',
            query_goal='BUILTIN',
            notices=[])

    result_solution = _execute(username, query_solution)
    if result_solution is None:
        return QueryResultMessage(
            message=f'Teacher-provided solution is not supported',
            query=NAME,
            query_type='BUILTIN',
            query_goal='BUILTIN',
            notices=[])

    # ensure both results have the same columns
    if not result_user.compare_column_names(result_solution):
        message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
        message += 'Your query has different columns from the solution. Cannot compare results.<br/>'
        message += f'Expected: <code>{"</code>, <code>".join([col.name for col in result_solution.columns])}</code><br/>'
        message += f'Your query: <code>{"</code>, <code>".join([col.name for col in result_user.columns])}</code><br/>'

        return QueryResultMessage(
            message=message,
            query=NAME,
            query_type='BUILTIN',
            query_goal='BUILTIN',
            notices=[])
    
    # check for wrong data types
    wrong_types = result_user.compare_column_types(result_solution)

    if wrong_types:
        message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
        message += 'Your query has different data types from the solution. Cannot compare results.<br/>'
        message += f'Expected: <code>{"</code>, <code>".join([f"{col.name}<i>({get_datatype_name(col.data_type)}</i>)" for col in result_solution.columns])}</code><br/>'
        message += f'Your query: <code>{"</code>, <code>".join([f"{col.name}<i>({get_datatype_name(col.data_type)}</i>)" for col in result_user.columns])}</code><br/>'

        return QueryResultMessage(
            message=message,
            query=NAME,
            query_type='BUILTIN',
            query_goal='BUILTIN')

    
    has_same_result, comparison = result_user.compare_results(result_solution)

    if has_same_result:
        return QueryResultMessage(
            message=f'<i class="fa fa-check text-success me-1" ></i>Solution is correct.',
            query=NAME,
            query_type='BUILTIN',
            query_goal='BUILTIN')
    else:
        return QueryResultDataset(
            result=comparison,
            query=NAME,
            columns=result_user.columns,
            query_type='BUILTIN',
            query_goal='BUILTIN')

