from IPython.core.interactiveshell import InteractiveShell
from dav_tools import messages
import psycopg2
import sys
import pandas as pd

import run_cell


def setup(username=None, password=None, host=None, database=None, allow_code_execution=False):
    run_cell.DB_USERNAME = username if username is not None else messages.ask('Enter database username', file=sys.stdout)
    run_cell.DB_PASSWORD = password if password is not None else messages.ask('Enter database password', file=sys.stdout)
    run_cell.DB_ADDRESS = host if host is not None else messages.ask('Enter database host', file=sys.stdout)
    run_cell.DB_NAME = database if database is not None else messages.ask('Enter database name', file=sys.stdout)

    if test_connection():
        messages.success('Database connection successful', file=sys.stdout)
    else:
        return

    # Display all DataFrame rows
    pd.set_option('display.max_rows', None)

    override_execution(allow_code_execution)


def test_connection():
    try:
        conn = psycopg2.connect(user=run_cell.DB_USERNAME, password=run_cell.DB_PASSWORD, host=run_cell.DB_ADDRESS, dbname=run_cell.DB_NAME)
        conn.close()

        return True
    except Exception as e:
        messages.error('Error connecting to the database:', e)
        return False


def override_execution(allow_code_execution=False):
    if allow_code_execution and not hasattr(InteractiveShell, 'run_cell_original'):
        InteractiveShell.run_cell_original = InteractiveShell.run_cell
        InteractiveShell.run_cell = run_cell.run_cell_sql_python
    else:
        InteractiveShell.run_cell = run_cell.run_cell_sql_only

    messages.success('SQL execution enabled', file=sys.stdout)
    if allow_code_execution:
        messages.warning(f'Only commands starting with {run_cell.SQL_COMMANDS} will be interpreted as SQL', file=sys.stdout)
    else:
        messages.info('All code executed from now on will be interpreted as SQL', file=sys.stdout)
