from .database import Database
from .postgresql import PostgresqlDatabase
from .mysql import MySQLDatabase

import os


def get_database(dbname: str, dbms: str) -> Database:
    '''Factory function to get the appropriate database backend.'''

    if dbms == 'postgresql':
        return PostgresqlDatabase(dbname)

    if dbms == 'mysql':
        return MySQLDatabase(dbname)

    raise ValueError(f'Unsupported DBMS: {dbms} ({dbname})')
