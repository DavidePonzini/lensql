from abc import ABC, abstractmethod
import datetime
from server.sql import SQLCode, SQLException, QueryResult, QueryResultDataset, QueryResultError, QueryResultMessage, Column
from typing import Any

from typing import Iterable

class DatabaseConnection(ABC):
    def __init__(self, dbname: str, username: str, autocommit: bool = True):
        self.dbname = dbname
        self.username = username
        self.autocommit = autocommit
        self.last_operation_ts = datetime.datetime.now()

    @abstractmethod
    def execute_sql(self, statement: SQLCode) -> Iterable[QueryResult]:
        '''Executes the given SQLCode statement and yields QueryResult objects.'''
        pass

    @abstractmethod
    def execute_sql_unsafe(self, statement: str) -> list[tuple[Any, ...]]:
        '''Executes the given SQL statement and returns the raw results as a list of tuples.'''
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

    def update_last_operation_ts(self) -> None:
        self.last_operation_ts = datetime.datetime.now()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()

    @property
    def time_since_last_operation(self) -> datetime.timedelta:
        return datetime.datetime.now() - self.last_operation_ts
    
    @property
    @abstractmethod
    def notices(self) -> list[str]:
        '''Returns the notices from the connection.'''
        pass

    @abstractmethod
    def clear_notices(self):
        '''Clears the notices from the connection.'''
        pass
