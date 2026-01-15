from .postgresql import PostgresqlDatabase

def start_cleanup_threads():
    '''Starts cleanup threads for all database backends.'''

    PostgresqlDatabase.start_cleanup_thread()
    # mysql.start_cleanup_thread()