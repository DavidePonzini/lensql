from . import connection

import datetime
import os
import threading
import time
from dav_tools import messages

MAX_CONNECTION_AGE = datetime.timedelta(hours=float(os.getenv('MAX_CONNECTION_HOURS', '4')))
CLEANUP_INTERVAL_SECONDS = int(os.getenv('CLEANUP_INTERVAL_SECONDS', '60'))


def _connection_cleanup_thread():
    connections = connection.connections
    conn_lock = connection.conn_lock

    while True:
        now = datetime.datetime.now()

        to_remove = [] # don't remove while iterating
        for username, conn in connections.items():
            if now - conn.last_operation_ts <= MAX_CONNECTION_AGE:
                continue

            to_remove.append(username)
        with conn_lock:
            for username in to_remove:
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
    cleanup_thread = threading.Thread(target=_connection_cleanup_thread, daemon=True)
    cleanup_thread.start()
    