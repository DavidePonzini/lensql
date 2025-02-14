from IPython.core.interactiveshell import InteractiveShell
from dav_tools import messages
import psycopg2
import sys
import pandas as pd

import run_sql


def setup(username, password, host, database, allow_code_execution=False):
    run_sql.DB_USERNAME = username
    run_sql.DB_PASSWORD = password
    run_sql.DB_ADDRESS = host
    run_sql.DB_NAME = database

    # Test connection
    try:
        conn = psycopg2.connect(user=run_sql.DB_USERNAME, password=run_sql.DB_PASSWORD, host=run_sql.DB_ADDRESS, dbname=run_sql.DB_NAME)
        conn.close()

        messages.success('Database connection successful', file=sys.stdout)
    except Exception as e:
        messages.error('Error connecting to the database:', e)
        return

    # Display all DataFrame rows
    pd.set_option('display.max_rows', None)

    # Override Jupyter execution
    if allow_code_execution and not hasattr(InteractiveShell, 'run_cell_original'):
        InteractiveShell.run_cell_original = InteractiveShell.run_cell

    InteractiveShell.run_cell = run_sql.run_cell
    messages.success('SQL execution enabled', file=sys.stdout)

    if allow_code_execution:
        messages.warning(f'Only commands starting with {run_sql.SQL_COMMANDS} will be interpreted as SQL', file=sys.stdout)
    else:
        messages.info('All code executed from now on will be interpreted as SQL', file=sys.stdout)
