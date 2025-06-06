import datetime
import os
import psycopg2
from threading import Lock
from dav_tools import messages

HOST        =       os.getenv('USER_DB_HOST', 'localhost')
PORT        =   int(os.getenv('USER_DB_PORT', '5432'))

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
    
def get_admin_connection(dbname: str = 'postgres', autocommit: bool = True) -> DBConnection:
    '''
    Returns the admin connection for the postgres user.
    This connection is not added to the connection pool.
    '''

    return DBConnection(dbname=dbname, username='postgres', autocommit=autocommit)