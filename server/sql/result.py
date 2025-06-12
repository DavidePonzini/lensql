from abc import ABC, abstractmethod
import pandas as pd

from server.sql.query_goal import QueryGoal
from .code import SQLException

class QueryResult(ABC):
    '''Represents the result of a SQL query.'''
    def __init__(self, query: str, success: bool, query_type: str, query_goal: QueryGoal, data_type: str, notices: list[str]):
        self.query = query
        self.success = success
        self.query_type = query_type
        self.query_goal = query_goal
        self.data_type = data_type
        self.notices = notices
        self.id = None

    @property
    @abstractmethod
    def result(self) -> str:
        '''Returns the result of the query as a string representation.'''
        pass
    
    def __repr__(self):
        return f'QueryResult(result="{self.result[:10]}", query="{self.query[:10]}", success={self.success})'
    
class QueryResultError(QueryResult):
    '''Represents the result of a SQL query that failed to execute.'''
    def __init__(self, exception: SQLException, query: str, query_type: str, query_goal: str, notices: list = []):
        super().__init__(
            query=query,
            success=False,
            query_type=query_type,
            query_goal=query_goal,
            notices=notices,
            data_type='message')
        self._result = exception

    @property
    def result(self) -> str:
        return str(self._result)

class QueryResultDataset(QueryResult):
    '''Represents the result of a SQL query that returned a dataset.'''
    def __init__(self, result: pd.DataFrame, query: str, query_type: str, query_goal: str, notices: list = []):
        super().__init__(
            query=query,
            success=True,
            query_type=query_type,
            query_goal=query_goal,
            notices=notices,
            data_type='dataset')
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
    def __init__(self, message: str, query: str, query_type: str, query_goal: str, notices: list = []):
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
