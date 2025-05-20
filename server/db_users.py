import datetime
import os
import threading
import time
import pandas as pd
import psycopg2
from threading import Lock
from typing import Iterable
from dav_tools import messages

from sql_code import SQLCode, SQLException, QueryResult, QueryResultDataset, QueryResultError, QueryResultMessage
from queries import Queries


HOST        =       os.getenv('USER_DB_HOST')
PORT        =   int(os.getenv('USER_DB_PORT'))

MAX_CONNECTION_AGE = datetime.timedelta(hours=float(os.getenv('MAX_CONNECTION_HOURS')))
CLEANUP_INTERVAL_SECONDS = int(os.getenv('CLEANUP_INTERVAL_SECONDS'))


class DBConnection:
    def __init__(self, dbname: str, username: str, autocommit: bool = True):
        self.dbname = dbname
        self.username = username
        self.autocommit = autocommit
        
        self.last_operation_ts = datetime.datetime.now()
        self.connection = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=dbname,
            user=username,
            password='' # Password is not needed for the db_users
        )

        self.connection.autocommit = autocommit

    def close(self):
        try:
            self.connection.close()
        except Exception as e:
            messages.error(f"Error closing connection for user {self.username}: {e}")

    def cursor(self):
        return self.connection.cursor()
    
    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()
    
    def update_last_operation_ts(self):
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
    def notices(self) -> list:
        '''Returns the notices from the connection.'''
        try:
            return self.connection.notices
        except AttributeError:
            # Handle the case where notices are not available
            return []
        
    def clear_notices(self):
        '''Clears the notices from the connection.'''
        try:
            self.connection.notices = []
        except AttributeError:
            # Handle the case where notices are not available
            pass
        

connections: dict[str, DBConnection] = {}
conn_lock = Lock()



def connection_cleanup_thread():
    while True:
        now = datetime.datetime.now()
        for username, conn in connections.items():
            if now - conn.last_operation_ts <= MAX_CONNECTION_AGE:
                continue
        
            with conn_lock:
                try:
                    connections[username].close()
                    del connections[username]
                    messages.info(f"Closed expired connection for user: {username}")
                except Exception as e:
                    messages.error(f"Error closing connection for user {username}: {e}")

        time.sleep(CLEANUP_INTERVAL_SECONDS)

def start_cleanup_thread():
    '''
    Starts a thread that will periodically check for expired connections
    and close them if they are older than MAX_CONNECTION_AGE.
    '''
    cleanup_thread = threading.Thread(target=connection_cleanup_thread, daemon=True)
    cleanup_thread.start()

def get_connection(username: str, autocommit: bool = True) -> DBConnection:
    '''
    Returns the connection for the given username.
    If the connection does not exist, it raises an exception.
    '''

    if username in connections:
        conn = connections[username]
        conn.clear_notices()
        return conn

    with conn_lock:
        conn = DBConnection(dbname=username, username=username, autocommit=autocommit)
        connections[username] = conn

        return conn
    

def execute_queries(username: str, query_str: str) -> Iterable[QueryResult]:
    '''
    Executes the given SQL queries and returns the results.
    The queries will be separated into individual statements.

    Parameters:
        username (str): The username of the database user.
        query_str (str): The SQL query string to execute. The query string can contain multiple SQL statements separated by semicolons.
    Returns:
        Iterable[QueryResult]: An iterable of QueryResult objects.
    '''

    for statement in SQLCode(query_str).strip_comments().split():
        try:
            conn = get_connection(username)
            with conn.cursor() as cur:
                cur.execute(statement.query)
                    
                if cur.description:  # Check if the query has a result set
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    yield QueryResultDataset(
                        result=pd.DataFrame(rows, columns=columns),
                        query=statement.query,
                        notices=conn.notices)
                    continue

                
                # No result set, return message status 
                # TODO return conn.notices
                yield QueryResultMessage(
                    message=f'{cur.statusmessage}',
                    query=statement.query,
                    notices=conn.notices)

            conn.update_last_operation_ts()
        except Exception as e:
            yield QueryResultError(
                exception=SQLException(e),
                query=statement.query,
                notices=conn.notices)
            try:
                conn.rollback()
                conn.update_last_operation_ts()
            except Exception as e:
                messages.error(f"Error rolling back connection for user {username}: {e}")

def run_builtin_query(username: str, query: Queries) -> QueryResult:
    '''Runs a builtin query and returns the result.'''

    try:
        conn = get_connection(username)
        with conn.cursor() as cur:
            cur.execute(query.value)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = pd.DataFrame(rows, columns=columns)


        conn.update_last_operation_ts()
        return QueryResultDataset(
            result=result,
            query=query.name,
            notices=conn.notices)
    except Exception as e:
        try:
            conn.rollback()
            conn.update_last_operation_ts()
        except Exception as e:
            messages.error(f"Error rolling back connection for user {username}: {e}")
        return QueryResultError(
            exception=SQLException(e),
            query=query.name,
            notices=conn.notices)

def list_schemas(username: str) -> QueryResult:
    '''Lists all schemas in the database.'''

    return run_builtin_query(username, Queries.LIST_SCHEMAS)

def list_tables(username: str) -> QueryResult:
    '''Lists tables in the current search_path.'''

    return run_builtin_query(username, Queries.LIST_TABLES)

def list_all_tables(username: str) -> QueryResult:
    '''Lists all tables in the database.'''

    return run_builtin_query(username, Queries.LIST_ALL_TABLES)

def list_constraints(username: str) -> QueryResult:
    '''Lists all constraints in the database.'''

    return run_builtin_query(username, Queries.LIST_CONSTRAINTS)

def show_search_path(username: str) -> QueryResult:
    '''Shows the search path for the database.'''

    return run_builtin_query(username, Queries.SHOW_SEARCH_PATH)

    