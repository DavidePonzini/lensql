import pandas as pd
from server.sql import QueryResult, QueryResultDataset, QueryResultMessage, SQLCode, Column


NAME = 'CHECK_SOLUTION'


class CheckSolutionResult:
    def __init__(self, correct: bool | None, execution_success: bool | None, result: QueryResult):
        self.correct = correct
        self.execution_success = execution_success
        self.result = result

    def __repr__(self):
        return f'CheckSolutionResult(correct={self.correct}, execution_success={self.execution_success})'

def result_message(correct: bool | None, execution_success: bool | None, message: str) -> CheckSolutionResult:
    query = SQLCode(NAME, builtin=True)
    result = QueryResultMessage(message, query=query)

    return CheckSolutionResult(
        correct=correct,
        execution_success=execution_success,
        result=result
    )

def result_dataset(correct: bool | None, execution_success: bool | None, result: pd.DataFrame, columns: list[Column]) -> CheckSolutionResult:
    query = SQLCode(NAME, builtin=True)
    dataset = QueryResultDataset(result=result, columns=columns, query=query)

    return CheckSolutionResult(
        correct=correct,
        execution_success=execution_success,
        result=dataset
    )

