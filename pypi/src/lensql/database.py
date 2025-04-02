import pandas as pd
import psycopg2
from psycopg2.extensions import connection
from dav_tools import messages

HOST = None
PORT = None
DBNAME = None
USERNAME = None
PASSWORD = None

def are_credentials_set():
    '''Checks if all database credentials are set.'''

    for cred in (HOST, PORT, DBNAME, USERNAME, PASSWORD):
        if cred is None:
            return False
    return True

def connect() -> connection:
    '''Opens a connection to the database.'''

    if not are_credentials_set():
        raise Exception('Database credentials not set')
    
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        user=USERNAME,
        password=PASSWORD
    )

def set_credentials(host: str, port: int, dbname: str, username: str, password: str) -> bool:
    '''Sets the database credentials and tests the connection.'''
    
    global HOST, PORT, DBNAME, USERNAME, PASSWORD

    HOST = host
    PORT = port
    DBNAME = dbname
    USERNAME = username
    PASSWORD = password

    try:
        conn = connect()
        conn.close()

        return True
    except Exception as e:
        messages.error('Error connecting to the database:', e)
        return False
    
def list_users() -> pd.DataFrame:
    '''Lists all users in the database.'''

    conn = connect()
    cur = conn.cursor()

    cur.execute(Queries.LIST_USERS)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = pd.DataFrame(rows, columns=columns)

    cur.close()
    conn.close()

    return result

def list_schemas() -> pd.DataFrame:
    '''Lists all schemas in the database.'''

    conn = connect()
    cur = conn.cursor()

    cur.execute(Queries.LIST_SCHEMAS)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = pd.DataFrame(rows, columns=columns)

    cur.close()
    conn.close()

    return result

def list_tables() -> pd.DataFrame:
    '''Lists all tables in the database.'''

    conn = connect()
    cur = conn.cursor()

    cur.execute(Queries.LIST_TABLES)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    result = pd.DataFrame(rows, columns=columns)

    cur.close()
    conn.close()

    return result


class Queries:
    LIST_USERS = '''
        -- LENSQL_BUILTIN
        SELECT
            usename AS username
        FROM
            pg_catalog.pg_user
        ORDER BY
            usename;
    '''

    LIST_SCHEMAS = '''
        -- LENSQL_BUILTIN
        SELECT
            schema_name,
            schema_owner
        FROM
            information_schema.schemata
        ORDER BY
            schema_name;
    '''

    LIST_TABLES = '''
        -- LENSQL_BUILTIN
        SELECT
            table_schema AS schema,
            table_name as table,
            table_type as type
        FROM
            information_schema.tables
        WHERE
            table_schema <> 'pg_catalog'
            AND table_schema <> 'information_schema'
        ORDER BY
            table_schema,
            table_name;
    '''