from .result import QueryResult

class QueryResultMessage(QueryResult):
    '''Represents the result of a SQL query that returned a message.'''
    def __init__(self, message: str, *,
                 query: str,
                 query_type: str, query_goal: str,
                 notices: list = []):
        super().__init__(
            query=query,
            success=True,
            query_type=query_type,
            query_goal=query_goal,
            notices=notices,
            data_type='message')
        self._result = message

    @property
    def result(self) -> str:
        return self._result
