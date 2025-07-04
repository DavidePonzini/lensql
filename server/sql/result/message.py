from .result import QueryResult
from ..code import SQLCode

class QueryResultMessage(QueryResult):
    '''Represents the result of a SQL query that returned a message.'''
    def __init__(self, message: str, *,
                 query: SQLCode,
                 notices: list = []):
        super().__init__(
            query=query,
            success=True,
            notices=notices,
            data_type='message')
        self._result = message

    @property
    def result_html(self) -> str:
        return self._result
    
    @property
    def result_text(self) -> dict:
        return self._result
        
