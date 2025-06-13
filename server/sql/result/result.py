from abc import ABC, abstractmethod

from ..query_goal import QueryGoal

class QueryResult(ABC):
    '''Represents the result of a SQL query.'''
    def __init__(self, *,
                 data_type: str,
                 query: str, success: bool,
                 query_type: str, query_goal: QueryGoal,
                 notices: list[str]):
        self.query = query
        self.success = success
        self.query_type = query_type
        self.query_goal = query_goal
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
    
