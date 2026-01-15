from abc import ABC, abstractmethod
from .database_connection import DatabaseConnection
import threading
import time
import datetime
import os
import dav_tools
from server.sql import SQLCode, QueryResult, SQLException, QueryResultError
from typing import Iterable

MAX_CONNECTION_AGE = datetime.timedelta(hours=float(os.getenv('MAX_CONNECTION_HOURS', '4')))
CLEANUP_INTERVAL_SECONDS = int(os.getenv('CLEANUP_INTERVAL_SECONDS', '60'))

class Database(ABC):
    connections: dict[str, DatabaseConnection] = {}
    conn_lock = threading.Lock()
    admin_username = ''

    def __init__(self, dbname: str):
        self.dbname = dbname

    def execute_sql(self, username: str, query_str: str, strip_comments: bool = True) -> Iterable[QueryResult]:
        '''
        Executes the given SQL queries and returns the results.
        The queries will be separated into individual statements.

        Parameters:
            username (str): The username of the database user.
            query_str (str): The SQL query string to execute. The query string can contain multiple SQL statements separated by semicolons.
        Returns:
            Iterable[QueryResult]: An iterable of QueryResult objects.
        '''
        for statement in SQLCode(query_str).split():
        
            # NOTE: do not `strip_comments` from the SQL code for very large queries
            #   as it takes the server too much time to parse the SQL code,
            #   causing a timeout error in the client.
            if strip_comments:
                statement = statement.strip_comments()

            conn = None
            try:
                conn = self.connect(username)

                yield from conn.execute_sql(statement.query)
                conn.update_last_operation_ts()
            except SQLException as e:
                if conn is None:
                    return # cannot rollback if no connection
                
                try:
                    conn.rollback()
                    conn.update_last_operation_ts()
                except Exception as e2: # catch all to avoid handling each DB exception separately
                    dav_tools.messages.error(f"Error rolling back connection for user {username}: {e2}")
                
                yield QueryResultError(
                    exception=e,
                    query=statement,
                    notices=conn.notices)

    @abstractmethod
    def init(self, password: str) -> bool:
        '''Initializes the database.'''
        pass

    @abstractmethod
    def exists(self) -> bool:
        '''Checks if the database exists.'''
        pass
    
    @abstractmethod
    def _get_connection(self, username: str, autocommit: bool = True) -> DatabaseConnection:
        '''Gets a connection for the specified user.'''
        pass

    def connect(self, username: str, autocommit: bool = True) -> DatabaseConnection:
        '''Connects to the database as the specified user.'''
        
        if username in self.connections:
            conn = self.connections[username]
            conn.clear_notices()
            return conn
        
        with self.conn_lock:
            conn = self._get_connection(username, autocommit=autocommit)
            self.connections[username] = conn
            return conn

    def connect_as_admin(self, autocommit: bool = True) -> DatabaseConnection:
        '''
            Connects to the database as the admin user.
            This connection is not added to the connection pool.
        '''
        return self._get_connection(self.admin_username, autocommit=autocommit)

    # region Cleanup
    @staticmethod
    def _connection_cleanup_thread() -> None:
        '''
        Thread that cleans up idle connections.
        '''
        while True:
            # Sleep first to avoid immediate cleanup on startup
            time.sleep(CLEANUP_INTERVAL_SECONDS)

            with Database.conn_lock:
                to_remove = []  # don't remove while iterating

                for username, conn in Database.connections.items():
                    if conn.time_since_last_operation.total_seconds() > 300:  # 5 minutes idle
                        conn.close()
                        to_remove.append(username)

                for username in to_remove:
                    try:
                        del Database.connections[username]
                        dav_tools.messages.info(f"Closed expired connection for user: {username}")
                    except Exception as e:
                        dav_tools.messages.error(f"Error closing connection for user {username}: {e}")

    @staticmethod
    def start_cleanup_thread() -> None:
        '''
            Starts a thread that will periodically check for expired connections
            and close them if they are older than MAX_CONNECTION_AGE.
        '''
        cleanup_thread = threading.Thread(target=Database._connection_cleanup_thread, daemon=True)
        cleanup_thread.start()
    # endregion