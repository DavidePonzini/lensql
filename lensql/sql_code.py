import sqlparse
from typing import Self


class SQLCode:
    def __init__(self, query: str):
        self.query = query

    def strip_comments(self) -> Self:
        '''Remove comments from the SQL query'''
        code = sqlparse.format(self.query, strip_comments=True)
        return SQLCode(code)

    def has_clause(self, clause: str) -> bool:
        '''Check if the SQL query has a specific clause'''
        return clause.upper() in self.query.upper()

    def __str__(self) -> str:
        return self.query