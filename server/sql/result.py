from abc import ABC, abstractmethod
import pandas as pd
from .code import SQLException

class QueryResult(ABC):
    '''Represents the result of a SQL query.'''
    def __init__(self, query: str, success: bool, notices: list[str], query_type: str):
        self.query = query
        self.success = success
        self.type = query_type
        self.notices = notices
        self.id = None

    @property
    @abstractmethod
    def result(self) -> str:
        pass
    
    def __repr__(self):
        return f'QueryResult(result="{self.result[:10]}", query="{self.query[:10]}", success={self.success})'

class QueryResultError(QueryResult):
    '''Represents the result of a SQL query that failed to execute.'''
    def __init__(self, exception: SQLException, query: str, notices: list = []):
        super().__init__(
            query=query,
            success=False,
            notices=notices,
            query_type='message')
        self._result = exception

    @property
    def result(self) -> str:
        return str(self._result)

class QueryResultDataset(QueryResult):
    '''Represents the result of a SQL query that returned a dataset.'''
    def __init__(self, result: pd.DataFrame, query: str, notices: list = []):
        super().__init__(
            query=query,
            success=True,
            notices=notices,
            query_type='dataset')
        self._result = result

    @property
    def result(self) -> str:
        result = self._result.replace({None: 'NULL'})

        result = result.to_html(
            classes='table table-bordered table-hover table-responsive',
            show_dimensions=True,
            border=0
        )
        result = result.replace('<thead>', '<thead class="table-dark">').replace('<tbody>', '<tbody class="table-group-divider">')
        return result

class QueryResultMessage(QueryResult):
    '''Represents the result of a SQL query that returned a message.'''
    def __init__(self, message: str, query: str, notices: list = []):
        super().__init__(
            query=query,
            success=True,
            notices=notices,
            query_type='message')
        self._result = message

    @property
    def result(self) -> str:
        return self._result
