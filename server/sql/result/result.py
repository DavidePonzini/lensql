from abc import ABC, abstractmethod

from ..code import SQLCode

class QueryResult(ABC):
    '''Represents the result of a SQL query.'''
    def __init__(self, *,
                 data_type: str,
                 query: SQLCode,
                 success: bool,
                 notices: list[str]):
        
        self.query = query
        '''The SQL code that was executed.'''

        self.success = success
        '''Whether the query executed successfully.'''

        self.data_type = data_type
        '''The type of data returned by the query.'''

        self.notices = notices
        '''Any notices or warnings generated during query execution.'''

        self.query_id: int | None = None

    @property
    @abstractmethod
    def result_html(self) -> str:
        '''Returns the result of the query as HTML.'''
        pass

    @property
    @abstractmethod
    def result_text(self) -> str:
        '''Returns the result of the query as a string.'''
        pass

    def __repr__(self):
        return f'QueryResult(result="{self.result_html[:10]}", query="{self.query.query[:10]}", success={self.success})'
    
