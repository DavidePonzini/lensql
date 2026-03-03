from ..connection import DatabaseConnection
import psycopg2
import os
import dav_tools
from server.sql import SQLCode, QueryResult, QueryResultDataset, QueryResultMessage, Column
import pandas as pd
from typing import Iterable
from .exception import PostgresqlException
from typing import Any

class PostgresqlConnection(DatabaseConnection):
    def __init__(self, host: str, port: int, autocommit: bool = True):
        super().__init__(host, port)
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            dbname='postgres',
            user='postgres',
            password='' # Password is set to trust in the container configuration
        )

        self.connection.autocommit = autocommit

    def close(self) -> None:
        super().close()

        try:
            self.connection.close()
        except Exception as e:
            dav_tools.messages.error(f"Error closing PostgreSQL connection for user database {self.host}: {e}")

    def is_open(self) -> bool:
        return self.connection and not self.connection.closed

    def cursor(self):
        return self.connection.cursor()
    
    def rollback(self) -> None:
        super().rollback()

        self.connection.rollback()

    def commit(self) -> None:
        super().commit()

        self.connection.commit()

    @property
    def notices(self) -> list[str]:
        return self.connection.notices
    
    def clear_notices(self) -> None:
        super().clear_notices()

        self.connection.notices.clear()

    def execute_sql(self, statement: SQLCode) -> Iterable[QueryResult]:
        super().execute_sql(statement)

        with self.cursor() as cur:
            try:
                cur.execute(statement.query)

                self.update_last_operation_ts()
                
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
            
    def execute_sql_raw(self, statement: str) -> list[tuple[Any, ...]]:
        super().execute_sql_raw(statement)

        with self.cursor() as cur:
            cur.execute(statement)

            self.update_last_operation_ts()

            if cur.description:     # Check if the query has a result set
                return cur.fetchall()
            return []
