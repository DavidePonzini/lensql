from .database import Database
from .postgresql import PostgresqlDatabase

import os


def get_database(dbname: str, dbms: str) -> Database:
    '''Factory function to get the appropriate database backend.'''

    if dbms == 'postgresql':
        return PostgresqlDatabase(dbname)

    # if dbms == 'mysql':
    #     return MySQLDatabase()

    raise ValueError(f'Unsupported DBMS: {dbms} ({dbname})')

def start_cleanup_threads():
    '''Starts cleanup threads for all database backends.'''

    PostgresqlDatabase.start_cleanup_thread()
    # mysql.start_cleanup_thread()