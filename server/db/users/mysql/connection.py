from ..connection import DatabaseConnection
import dav_tools
from server.sql import SQLCode, QueryResult, QueryResultDataset, QueryResultMessage, Column
import pandas as pd
from typing import Iterable, Any

import mysql.connector
from mysql.connector import Error as MySQLError

from .exception import MySQLException


class MySQLConnection(DatabaseConnection):
    def __init__(self, host: str, port: int, autocommit: bool = True):
        super().__init__(host, port)

        # Match your container defaults: root / password (set in container env)
        self.connection = mysql.connector.connect(
            host=host,
            port=port,
            database='default',
            user='root',
            password='',
            autocommit=autocommit,
        )

    def close(self) -> None:
        super().close()

        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            dav_tools.messages.error(f'Error closing MySQL connection for user database {self.host}: {e}')

    def is_open(self) -> bool:
        # Quick local check first
        try:
            if not self.connection or not self.connection.is_connected():
                return False
        except Exception:
            return False

        # Active check: forces a round-trip to the server
        try:
            cur = self.connection.cursor()
            try:
                cur.execute('SELECT 1;')
                cur.fetchone()
            finally:
                cur.close()
            return True
        except MySQLError:
            # The connection is broken/stale (e.g., container restarted)
            try:
                self.connection.close()
            except Exception:
                pass
            return False

    def cursor(self):
        # buffered=True allows fetchall() safely even if unread results exist
        return self.connection.cursor(buffered=True)

    def rollback(self) -> None:
        super().rollback()
        self.connection.rollback()

    def commit(self) -> None:
        super().commit()
        self.connection.commit()

    @property
    def notices(self) -> list[str]:
        # MySQL connector doesn't expose PostgreSQL-like "notices"
        return []

    def clear_notices(self) -> None:
        super().clear_notices()
        # Nothing to clear for MySQL

    def execute_sql(self, statement: SQLCode) -> Iterable[QueryResult]:
        super().execute_sql(statement)

        with self.cursor() as cur:
            try:
                cur.execute(statement.query)

                if cur.description:  # query returned a result set
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]

                    yield QueryResultDataset(
                        result=pd.DataFrame(rows, columns=columns),
                        columns=[
                            Column(name=desc[0], data_type=desc[1])
                            for desc in cur.description
                        ] if cur.description else [],
                        query=statement,
                        notices=self.notices,
                    )
                    return

                # No result set -> return a message
                # MySQL doesn't have cur.statusmessage; provide something stable.
                yield QueryResultMessage(
                    message=f'OK ({cur.rowcount} rows affected)',
                    query=statement,
                    notices=self.notices,
                )
            except MySQLError as e:
                raise MySQLException(e) from e

    def execute_sql_raw(self, statement: str) -> list[tuple[Any, ...]]:
        super().execute_sql_raw(statement)

        with self.cursor() as cur:
            cur.execute(statement)

            if cur.description:
                return cur.fetchall()
            return []