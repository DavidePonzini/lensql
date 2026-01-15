from ..connection import DatabaseConnection
import psycopg2
import os
import dav_tools
from server.sql import SQLCode, QueryResult, QueryResultDataset, QueryResultMessage, Column
import pandas as pd
from typing import Iterable
from .exception import PostgresqlException
from typing import Any

HOST        =       os.getenv('USER_DB_HOST_POSTGRES', 'localhost')
PORT        =   int(os.getenv('USER_DB_PORT_POSTGRES', '5432'))

class PostgresqlConnection(DatabaseConnection):
    def __init__(self, dbname: str, username: str, autocommit: bool = True):
        super().__init__(dbname, username)
        self.connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=dbname,
            user=username,
            password='' # Password is not needed for the db_users_postgres
        )

        self.connection.autocommit = autocommit

    def close(self) -> None:
        try:
            self.connection.close()
        except Exception as e:
            dav_tools.messages.error(f"Error closing PostgreSQL connection for user {self.username}: {e}")

    def cursor(self):
        return self.connection.cursor()
    
    def rollback(self) -> None:
        self.connection.rollback()

    def commit(self) -> None:
        self.connection.commit()

    @property
    def notices(self) -> list[str]:
        return self.connection.notices
    
    def clear_notices(self) -> None:
        self.connection.notices.clear()

    def execute_sql(self, statement: SQLCode) -> Iterable[QueryResult]:
        with self.cursor() as cur:
            try:
                cur.execute(statement.query)
                
                if cur.description:     # Check if the query has a result set
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]

                    yield QueryResultDataset(
                        result=pd.DataFrame(rows, columns=columns),
                        columns=[Column(name=col.name, data_type=col.type_code) for col in cur.description] if cur.description else [],
                        query=statement,
                        notices=self.notices)
                    return

                # No result set, return message status 
                yield QueryResultMessage(
                    message=f'{cur.statusmessage}',
                    query=statement,
                    notices=self.notices)
            except psycopg2.Error as e:
                raise PostgresqlException(e) from e
            
    def execute_sql_unsafe(self, statement: str) -> list[tuple[Any, ...]]:
        with self.cursor() as cur:
            cur.execute(statement)

            self.update_last_operation_ts()

            return cur.fetchall()
