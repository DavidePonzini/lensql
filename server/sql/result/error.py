from ..code import SQLCode
from ..exception import SQLException

from .result import QueryResult

class QueryResultError(QueryResult):
    '''Represents the result of a SQL query that failed to execute.'''
    def __init__(self, exception: SQLException, *,
                 query: SQLCode,
                 notices: list = []):
        super().__init__(
            query=query,
            success=False,
            notices=notices,
            data_type='message')
        self._result = exception

    @property
    def result_html(self) -> str:
        return str(self._result)

    @property
    def result_text(self) -> str:
        if self._result.error_code:
            return f'Message: {self._result}\nError Code: {self._result.error_code}'
        else:
            return f'Message: {self._result}'