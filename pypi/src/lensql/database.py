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