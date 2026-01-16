from dataclasses import dataclass
import pandas as pd
from server.sql import QueryResult, QueryResultDataset, QueryResultMessage, SQLCode, Column
from abc import ABC, abstractmethod


NAME = 'CHECK_SOLUTION'


class CheckExecutionStatus:
    '''Class representing the status of a solution check.'''
    def __init__(self, correct: bool | None, execution_success: bool | None, result: QueryResult):
        self.correct = correct
        self.execution_success = execution_success
        self.result = result

    def __repr__(self):
        return f'CheckExecutionStatus(correct={self.correct}, execution_success={self.execution_success})'

def result_message(correct: bool | None, execution_success: bool | None, message: str) -> CheckExecutionStatus:
    query = SQLCode(NAME, builtin=True)
    result = QueryResultMessage(message, query=query)

    return CheckExecutionStatus(
        correct=correct,
        execution_success=execution_success,
        result=result
    )

def result_dataset(correct: bool | None, execution_success: bool | None, result: pd.DataFrame, columns: list[Column]) -> CheckExecutionStatus:
    query = SQLCode(NAME, builtin=True)
    dataset = QueryResultDataset(result=result, columns=columns, query=query)

    return CheckExecutionStatus(
        correct=correct,
        execution_success=execution_success,
        result=dataset
    )

@dataclass
class CheckResult(ABC):
    '''Base class for the result of a solution check.'''
    correct: bool | None
    execution_success: bool | None

    @abstractmethod
    def to_result(self) -> CheckExecutionStatus:
        pass

@dataclass
class CheckResultMessage(CheckResult):
    '''A check result that returns a message, either for errors or success.'''
    message: str

    def to_result(self) -> CheckExecutionStatus:
        return result_message(self.correct, self.execution_success, self.message)

@dataclass
class CheckResultDataset(CheckResult):
    '''A check result that returns a dataset, for comparing user vs expected results.'''
    result: pd.DataFrame
    columns: list[Column]

    def to_result(self) -> CheckExecutionStatus:
        return result_dataset(self.correct, self.execution_success, self.result, self.columns)