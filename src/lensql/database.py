import psycopg2
from psycopg2.extensions import connection
from dav_tools import database, messages
import os

HOST = None
PORT = None
DBNAME = None

USERNAME = None
PASSWORD = None

def are_credentials_set():
    for cred in (HOST, PORT, DBNAME, USERNAME, PASSWORD):
        if cred is None:
            return False
    return True

def connect() -> connection:
    if not are_credentials_set():
        raise Exception('Database credentials not set')
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        user=USERNAME,
        password=PASSWORD
    )

def logger_connect() -> database.PostgreSQL:
    conn = database.PostgreSQL(
        host=       os.getenv('LENSQL_LOGGER_HOST'),
        port=   int(os.getenv('LENSQL_LOGGER_PORT')),
        database=   os.getenv('LENSQL_LOGGER_DBNAME'),
        user=       os.getenv('LENSQL_LOGGER_USER'),
        password=   os.getenv('LENSQL_LOGGER_PASSWORD')
    )

    return conn

def test_connection():
    try:
        conn = connect()
        conn.close()

        return True
    except Exception as e:
        messages.error('Error connecting user to the database:', e)
        return False
    
def test_logger_connection():
    try:
        with logger_connect().connect():
            pass

        return True
    except Exception as e:
        messages.error('Error connecting to the database:', e)
        return False