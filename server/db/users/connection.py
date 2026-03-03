from abc import ABC, abstractmethod
import datetime
from server.sql import SQLCode, SQLException, QueryResult, QueryResultDataset, QueryResultError, QueryResultMessage, Column
from typing import Any

from typing import Iterable


import dav_tools

class DatabaseConnection(ABC):
    def __init__(self, host: str, port: int, autocommit: bool = True):
        self.host = host
        self.port = port
        self.autocommit = autocommit
        self.last_operation_ts = datetime.datetime.now()

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

    def update_last_operation_ts(self) -> None:
        self.last_operation_ts = datetime.datetime.now()

    def __enter__(self):
        dav_tools.messages.debug(f'{id(self)} Opened connection for user database {self.host}')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

        self.close()
        dav_tools.messages.debug(f'{id(self)} Closed connection for user database {self.host}')

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
