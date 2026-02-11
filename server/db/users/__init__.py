from .database import Database
from .postgresql import PostgresqlDatabase

import os


def get_database(dbname: str, db_type: str) -> Database:
    '''Factory function to get the appropriate database backend.'''

    # TODO: temporary implementation, always return PostgresqlDatabase for now. In the future, we can add support for other databases like MySQL, SQLite, etc. based on the db_type parameter.
    return PostgresqlDatabase(dbname)

    if db_type == 'postgresql':
        return PostgresqlDatabase(dbname)
    # elif db_type == 'mysql':
    #     return MySQLDatabase()
    else:
        raise ValueError(f'Unsupported database type: {db_type}')

def start_cleanup_threads():
    '''Starts cleanup threads for all database backends.'''

    PostgresqlDatabase.start_cleanup_thread()
    # mysql.start_cleanup_thread()