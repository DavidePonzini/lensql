import psycopg2
from psycopg2.extensions import connection
from dav_tools import database

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
        host='ponzidav.com',
        port=5432,
        database='postgres',
        user='lensql',
        password='lensql_pwd'
    )

    return conn