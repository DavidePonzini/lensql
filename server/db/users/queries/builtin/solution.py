import pandas as pd
from dav_tools import messages
from flask_babel import _

from . import util
from server.sql import QueryResult, QueryResultDataset, QueryResultMessage, SQLCode, Column, get_datatype_name
from ...connection import get_connection

NAME = 'CHECK_SOLUTION'


class CheckSolutionResult:
    def __init__(self, correct: bool | None, execution_success: bool | None, result: QueryResult):
        self.correct = correct
        self.execution_success = execution_success
        self.result = result

    def __repr__(self):
        return f'CheckSolutionResult(correct={self.correct}, execution_success={self.execution_success}'

def _result_message(correct: bool | None, execution_success: bool | None, message: str) -> CheckSolutionResult:
    query = SQLCode(NAME, builtin=True)
    result = QueryResultMessage(message, query=query)

    return CheckSolutionResult(
        correct=correct,
        execution_success=execution_success,
        result=result
    )

def _result_dataset(correct: bool | None, execution_success: bool | None, result: pd.DataFrame, columns: list[Column]) -> CheckSolutionResult:
    query = SQLCode(NAME, builtin=True)
    dataset = QueryResultDataset(result=result, columns=columns, query=query)

    return CheckSolutionResult(
        correct=correct,
        execution_success=execution_success,
        result=dataset
    )

def _execute(username: str, query: str) -> tuple[QueryResultDataset | None, bool]:
    '''
        Execute the first statement of the query and return the result.

        Returns:
            QueryResultDataset: The result of the query execution.
            bool: True if the query was executed successfully, False otherwise. None if the query was not executed (e.g. not a SELECT query).
    '''

    statements = SQLCode(query).split()

    # Only execute the first statement
    statement = util.next_statement(statements)
    if statement is None:
        return None, None

    # Only SELECT queries are supported
    if statement.query_type != 'SELECT':
        return None, None
    try:
        conn = get_connection(username)
        
        with conn.cursor() as cur:
            cur.execute(statement.query)
            conn.update_last_operation_ts()

            # If the query doesn't have a result set, we don't need it   
            if not cur.description:
                return None, True

            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]

            return QueryResultDataset(
                result=pd.DataFrame(rows, columns=columns),
                columns=[Column(name=col.name, data_type=col.type_code) for col in cur.description] if cur.description else [],
                query=statement,
                notices=conn.notices), True

    except Exception as e:
        try:
            conn.rollback()
            conn.update_last_operation_ts()
        except Exception as e:
            messages.error(f"Error rolling back connection for user {username}: {e}")
        return None, False

def check(username: str, query_user: str, query_solution: str) -> CheckSolutionResult:
    '''
    Checks the user's solution against the exercise solution.
    If multiple queries are present, only the first one is checked.
    If the exercise has no solution, a message is returned.
    Args:
        username (str): The username of the user.
        query_user (str): The SQL query submitted by the user.
        solution (str): The SQL solution for the exercise.

    Returns:
        tuple: A tuple containing a boolean indicating if the solution is correct and a QueryResult object.
        If the solution is correct, the QueryResult object contains a success message.
        If the solution is incorrect, the QueryResult object contains the comparison of results.
        If the exercise has no solution, a message indicating that is returned.
    '''

    if not query_solution:
        message = _('No solution found for this exercise.')
        return _result_message(None, None, message)

    result_user, execution_success = _execute(username, query_user)
    if result_user is None:
        message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
        message += _('Your query is not supported. Please ensure it is a valid SQL SELECT query.')
        return _result_message(False, execution_success, message)

    result_solution, execution_success_solution = _execute(username, query_solution)
    if result_solution is None:
        message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
        message += _('Teacher-provided solution is not supported.')
        return _result_message(None, execution_success, message)

    # ensure both results have the same columns
    if not result_user.compare_column_names(result_solution):
        message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
        message += _('Your query has different columns from the solution. Cannot compare results.') + '<br/>'
        message += _('Expected:') + f' <code>{"</code>, <code>".join([col.name for col in result_solution.columns])}</code><br/>'
        message += _('Your query:') + f' <code>{"</code>, <code>".join([col.name for col in result_user.columns])}</code><br/>'

        return _result_message(False, execution_success, message)

    # check for wrong data types
    wrong_types = result_user.compare_column_types(result_solution)

    if wrong_types:
        message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
        message += _('Your query has different data types from the solution. Cannot compare results.') + '<br/>'
        message += _('Expected:') + f' <code>{"</code>, <code>".join([f"{col.name}<i>({get_datatype_name(col.data_type)}</i>)" for col in result_solution.columns])}</code><br/>'
        message += _('Your query:') + f' <code>{"</code>, <code>".join([f"{col.name}<i>({get_datatype_name(col.data_type)}</i>)" for col in result_user.columns])}</code><br/>'

        return _result_message(False, execution_success, message)

    has_same_result, comparison = result_user.compare_results(result_solution)

    if has_same_result:
        message = '<i class="fa fa-check text-success me-1"></i>'
        message += _('Solution is correct.') + '<br/>'
        return _result_message(True, execution_success, message)
    else:
        return _result_dataset(False, execution_success, result=comparison, columns=result_user.columns)

