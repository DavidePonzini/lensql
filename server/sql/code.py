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

        expandable_types = {'CREATE', 'ALTER', 'DROP'}
        expandable_types_keywords = {
            'TABLE', 'VIEW', 'INDEX', 'SEQUENCE', 'FUNCTION', 'PROCEDURE',
            'TRIGGER', 'USER', 'ROLE', 'DATABASE', 'SCHEMA',
        }

        allowed_types = {
            'SET', 'SHOW', 'RESET',
            'EXPLAIN',
            'ANALYZE',
            'DO', 'CALL',
            'COPY',
            'CLUSTER',
            'GRANT', 'REVOKE',
            'BEGIN', 'COMMIT', 'ROLLBACK', 'ABORT',
        }


        statement = sqlparse.parse(self.query)[0]
        query_type = statement.get_type()

        # CREATE OR REPLACE is treated as CREATE
        if query_type == 'CREATE OR REPLACE':
            query_type = 'CREATE'

        # For expandable types, we need to determine the specific type of statement
        if query_type in expandable_types:
            # get type of create/alter/drop statement
            tokens = [t for t in statement.flatten() if t.ttype not in (sqlparse.tokens.Whitespace, sqlparse.tokens.Comment)]

            for i, token in enumerate(tokens):
                if token.ttype is sqlparse.tokens.DDL and token.normalized in expandable_types:
                    # Look ahead for the next Keyword (e.g. TABLE, VIEW, FUNCTION, USER...)
                    for next_token in tokens[i+1:]:
                        if next_token.ttype in (sqlparse.tokens.Keyword, sqlparse.tokens.DDL) and next_token.normalized in expandable_types_keywords:
                            next_token_str = next_token.normalized
                            return f'{query_type} {next_token_str}'
                    break

        # Extract more types
        if query_type == 'UNKNOWN':
            first_token = statement.token_first(skip_cm=True, skip_ws=True)
            if first_token and first_token.ttype in (sqlparse.tokens.Keyword, sqlparse.tokens.Token.Keyword.DCL):
                if first_token.normalized in allowed_types:
                    query_type = first_token.normalized.upper()

                    # If it's an EXPLAIN statement, check if it has ANALYZE
                    if query_type == 'EXPLAIN':
                        next_token = statement.token_next(statement.token_index(first_token), skip_cm=True, skip_ws=True)[1]
                        if next_token and next_token.normalized == 'ANALYZE':
                            query_type = 'EXPLAIN ANALYZE'

        return query_type

class SQLException:
    def __init__(self, exception: Exception):
        self.exception = exception

        self.name = type(self.exception).__name__

        message = str(self.exception.args[0]) if self.exception.args else ''
        self.description = message.splitlines()[0]
        self.traceback = message.splitlines()[1:]
    
    def __str__(self):
        return f'{self.name}: {self.description}'
