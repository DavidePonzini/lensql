from abc import ABC, abstractmethod
from server.sql import SQLCode, QueryResult
from typing import Any

from typing import Iterable


class DatabaseConnection(ABC):
    def __init__(self, host: str, port: int, autocommit: bool = True):
        self.host = host
        self.port = port
        self.autocommit = autocommit

    @abstractmethod
    def execute_sql(self, statement: SQLCode) -> Iterable[QueryResult]:
        '''Executes the given SQLCode statement and yields QueryResult objects.'''

        pass

    @abstractmethod
    def execute_sql_raw(self, statement: str) -> list[tuple[Any, ...]]:
        '''Executes the given SQL statement and returns the raw results as a list of tuples.'''
        pass

    @abstractmethod
    def is_open(self) -> bool:
        '''Returns True if the connection is open, False otherwise.'''
        pass

    @abstractmethod
    def close(self) -> None:
        '''Closes the database connection.'''
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        '''Rolls back the current transaction.'''
        pass

    @abstractmethod
    def commit(self) -> None:
        '''Commits the current transaction.'''
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

        self.close()

    @property
    @abstractmethod
    def notices(self) -> list[str]:
        '''Returns the notices from the connection.'''
        pass

    @abstractmethod
    def clear_notices(self):
        '''Clears the notices from the connection.'''
        pass
