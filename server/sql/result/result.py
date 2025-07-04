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
        self.success = success
        self.data_type = data_type
        self.notices = notices
        self.id = None

    @property
    @abstractmethod
    def result_html(self) -> str:
        '''Returns the result of the query as HTML.'''
        pass

    @property
    @abstractmethod
    def result_text(self) -> dict | None:
        '''Returns the result of the query as a dictionary.'''
        pass

    def __repr__(self):
        return f'QueryResult(result="{self.result_html[:10]}", query="{self.query[:10]}", success={self.success})'
    
