from .database import Database
from .postgresql import PostgresqlDatabase
from .mysql import MySQLDatabase
from sqlscope import Dialect


def get_database(dbname: str, dbms: Dialect) -> Database:
    '''Factory function to get the appropriate database backend.'''

    if dbms == Dialect.POSTGRES:
        return PostgresqlDatabase(dbname)

    if dbms == Dialect.MYSQL:
        return MySQLDatabase(dbname)

    raise ValueError(f'Unsupported DBMS: {dbms} ({dbname})')
