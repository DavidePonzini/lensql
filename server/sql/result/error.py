from ..exception import SQLException
import json

from .result import QueryResult

class QueryResultError(QueryResult):
    '''Represents the result of a SQL query that failed to execute.'''
    def __init__(self, exception: SQLException, *,
                 query: str,
                 query_type: str, query_goal: str,
                 notices: list = []):
        super().__init__(
            query=query,
            success=False,
            query_type=query_type,
            query_goal=query_goal,
            notices=notices,
            data_type='message')
        self._result = exception

    @property
    def result_html(self) -> str:
        return str(self._result)

    @property
    def result_text(self) -> dict:
        return self.result_html