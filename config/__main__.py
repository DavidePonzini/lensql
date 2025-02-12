from IPython.core.interactiveshell import InteractiveShell
from dav_tools import messages
import psycopg2
import sys
import pandas as pd

import sql


def setup(username, password, host, database):
    sql.DB_USERNAME = username
    sql.DB_PASSWORD = password
    sql.DB_ADDRESS = host
    sql.DB_NAME = database

    # Test connection
    try:
        conn = psycopg2.connect(user=sql.DB_USERNAME, password=sql.DB_PASSWORD, host=sql.DB_ADDRESS, dbname=sql.DB_NAME)
        conn.close()

        messages.success('Database connection successful', file=sys.stdout)
    except Exception as e:
        messages.error('Error connecting to the database:', e)
        return

    # Save original run_cell method
    # Only perform this operation once, to prevent infinite recursion
    if not hasattr(InteractiveShell, 'original_run_cell'):
        InteractiveShell.original_run_cell = InteractiveShell.run_cell

    # Override Jupyter execution
    InteractiveShell.run_cell = sql.auto_execute_sql
    messages.success('SQL execution enabled', file=sys.stdout)

    # Display all DataFrame rows
    pd.set_option('display.max_rows', None)
