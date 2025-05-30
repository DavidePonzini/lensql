import sqlparse
from typing import Iterable, Self

from ._sql_tokens import allowed_types


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
    
    @property
    def query_type(self) -> str:
        '''Get the type of the SQL query (e.g., SELECT, INSERT, UPDATE, DELETE)'''

        try:
            statement = sqlparse.parse(self.query)[0]
            first_token = statement.token_first(skip_cm=True)

            while type(first_token) is sqlparse.sql.Parenthesis:
                # If the first token is a parenthesis, we need to get the token inside it (skipping the parenthesis itself)
                first_token = first_token.token_next(0, skip_cm=True)[1]
            first_token_str = first_token.value.upper()

            # Categorization errors or unusual statements
            if first_token_str not in allowed_types:
                return 'OTHER'
            
            # We need an additional token to differentiate these statements
            if first_token_str in {'CREATE', 'ALTER', 'DROP'}:
                second_token = statement.token_next(0, skip_cm=True)[1]
                second_token_str = second_token.value.upper()
                return f'{first_token_str} {second_token_str}'
            
            return first_token_str
        except Exception as e:
            return 'UNKNOWN'

class SQLException:
    def __init__(self, exception: Exception):
        self.exception = exception

        self.name = type(self.exception).__name__

        message = str(self.exception.args[0]) if self.exception.args else ''
        self.description = message.splitlines()[0]
        self.traceback = message.splitlines()[1:]
    
    def __str__(self):
        return f'{self.name}: {self.description}'
