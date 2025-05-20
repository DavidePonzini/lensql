import sqlparse
from typing import Iterable, Self
from abc import ABC, abstractmethod
import pandas as pd


# Maximum length of SQL code to strip comments from
STRIP_COMMENTS_MAX_LENGTH = 1000


class SQLCode:
    def __init__(self, query: str):
        self.query = query

    def strip_comments(self, *, force: bool = False) -> Self:
        '''
            Remove comments from the SQL query
            If the query is too long, it will not be stripped unless force is set to True.
            This is to avoid performance issues with very large queries.

            Parameters:
                force (bool): If True, strip comments even if the query is too long.
            Returns:
                SQLCode: A new SQLCode object with comments stripped.
        '''

        if len(self.query) > STRIP_COMMENTS_MAX_LENGTH and not force:
            return self
        
        code = sqlparse.format(self.query, strip_comments=True)
        return SQLCode(code)

    def has_clause(self, clause: str) -> bool:
        '''Check if the SQL query has a specific clause'''
        return clause.upper() in self.query.upper()

    def split(self) -> Iterable[Self]:
        '''Split the SQL query into individual statements'''
        for query in sqlparse.split(self.query, strip_semicolon=False):
            yield SQLCode(query)
    
    @property
    def first_token(self) -> str:
        statement = sqlparse.parse(self.query)[0]
        first_token = statement.token_first(skip_cm=True)
        
        if first_token:
            return first_token.value.upper()
        
        return None


    def __str__(self) -> str:
        return self.query
    
class SQLException:
    def __init__(self, exception: Exception):
        self.exception = exception

        self.name = type(self.exception).__name__

        message = str(self.exception.args[0]) if self.exception.args else ''
        self.description = message.splitlines()[0]
        self.traceback = message.splitlines()[1:]
    
    def __str__(self):
        return f'{self.name}: {self.description}'

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
