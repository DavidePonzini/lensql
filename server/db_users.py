import os
import pandas as pd
import psycopg2
from psycopg2.extensions import connection
from threading import Lock
from dav_tools import messages

from sql_code import SQLCode, SQLException, QueryResult, QueryResultDataset, QueryResultError, QueryResultMessage
from queries import Queries

HOST        =       os.getenv('USER_DB_HOST')
PORT        =   int(os.getenv('USER_DB_PORT'))


connections: dict[str, connection] = {}
conn_lock = Lock()

def get_connection(username: str) -> connection:
    '''
    Returns the connection for the given username.
    If the connection does not exist, it raises an exception.
    '''

    with conn_lock:
        if username in connections:
            return connections[username]
        raise Exception(f'User {username} does not have a connection to the database.')
    
def create_connection(username: str, password: str, autocommit: bool = True) -> connection | None:
    '''
    Returns a connection to the database for the given username.
    If the connection does not exist, it creates a new one.
    '''

    with conn_lock:
        if username in connections:
            return connections[username]
        
        try:
            conn = psycopg2.connect(
                host=HOST,
                port=PORT,
                dbname=username,
                user=username,
                password=password
            )

            conn.autocommit = autocommit

            connections[username] = conn
            return conn
        except Exception as e:
            messages.error('Error connecting to the database:', e)
            return None

def execute_queries(username: str, query_str: str) -> list[QueryResult]:
    '''
    Executes the given SQL queries and returns the results.
    The queries will be separated into individual statements.

    Parameters:
        query (str): The SQL query to execute.

    Returns:
        pd.DataFrame | str | SQLException: The result of the query.
        str: The original query string.
        bool: True if the query was successful, False otherwise.
    '''

    result = []
    for statement in SQLCode(query_str).strip_comments().split():
        try:
            conn = get_connection(username)
            with conn.cursor() as cur:
                cur.execute(statement.query)
                    
                if cur.description:  # Check if the query has a result set
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    result.append(QueryResultDataset(pd.DataFrame(rows, columns=columns), statement.query))
                    continue
                
                # No result set, return the number of affected rows
                if cur.rowcount >= 0:
                    result.append(QueryResultMessage(f'{statement.first_token} {cur.rowcount}', statement.query))
                    continue

                # No number of affected rows, return the first token of the statement
                result.append(QueryResultMessage(f'{statement.first_token}', statement.query))
        except Exception as e:
            result.append(QueryResultError(SQLException(e), statement.query))
            conn.rollback()
        finally:
            cur.close()

    return result

def run_builtin_query(username: str, query: Queries) -> QueryResult:
    '''Runs a builtin query and returns the result.'''

    try:
        conn = get_connection(username)
        with conn.cursor() as cur:
            cur.execute(query.value)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = pd.DataFrame(rows, columns=columns)

        return QueryResultDataset(result, query.name)
    except Exception as e:
        conn.rollback()
        return QueryResultError(SQLException(e), query.name)

def list_schemas(username: str) -> QueryResult:
    '''Lists all schemas in the database.'''

    return run_builtin_query(username, Queries.LIST_SCHEMAS)

def list_tables(username: str) -> QueryResult:
    '''Lists all tables in the database.'''

    return run_builtin_query(username, Queries.LIST_TABLES)

