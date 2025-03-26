'''
This module contains the functions to configure the database connection and enable SQL execution in the notebook.
'''

from . import run_cell
from . import credentials

from IPython.core.interactiveshell import InteractiveShell
from dav_tools import messages
import psycopg2
import sys
import pandas as pd


def setup(host: str | None = None, port: int = 5432, database: str | None = None, username: str | None = None, *,  allow_code_execution=False):
    '''Configures the database connection and enables SQL execution in the notebook.'''
    credentials.HOST = host if host is not None else messages.ask('Enter database host', file=sys.stdout)
    credentials.PORT = port if port is not None else messages.ask('Enter database port', file=sys.stdout)
    credentials.DBNAME = database if database is not None else messages.ask('Enter database name', file=sys.stdout)
    credentials.USERNAME = username if username is not None else messages.ask('Enter database username', file=sys.stdout)
    credentials.PASSWORD = messages.ask('Enter database password', secret=True, file=sys.stdout)

    if test_connection():
        messages.success('Database connection successful', file=sys.stdout)
    else:
        return

    # Display all DataFrame rows
    pd.set_option('display.max_rows', None)

    override_execution(allow_code_execution)


def test_connection():
    try:
        conn = psycopg2.connect(
            host=credentials.HOST,
            port=credentials.PORT,
            dbname=credentials.DBNAME,
            user=credentials.USERNAME,
            password=credentials.PASSWORD
        )
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
