'''
This module contains the functions to configure the database connection and enable SQL execution in the notebook.
'''

from . import run_cell

from .. import database
from .. import server

from IPython.core.interactiveshell import InteractiveShell
from dav_tools import messages
import sys
import pandas as pd
import os

def setup(
        host:       str =       os.getenv('LENSQL_HOST',        ''),
        username:   str =       '',
        dbhost:     str =       os.getenv('LENSQL_DB_HOST',     ''),
        dbport:     int =   int(os.getenv('LENSQL_DB_PORT',     '5432')),
        dbname:     str =       os.getenv('LENSQL_DB_NAME',     ''),
        dbusername: str =       os.getenv('LENSQL_DB_USERNAME', ''),
        dbpassword: str =       os.getenv('LENSQL_DB_PASSWORD', ''),
        *, allow_code_execution=False):
    '''Configures the database connection and enables SQL execution in the notebook.'''
    while len(host) == 0: 
        host = messages.ask('Enter server host', file=sys.stdout)
    while len(username) == 0:
        username = messages.ask('Enter server username', file=sys.stdout)

    if server.login(host, username):
        messages.success('Server is online', file=sys.stdout)
    else:
        return
    
    while len(dbhost) == 0:
        dbhost = messages.ask('Enter database host', file=sys.stdout)
    while dbport is None:
        dbport = messages.ask('Enter database port', file=sys.stdout)
    while len(dbname) == 0:
        dbname = messages.ask('Enter database name', file=sys.stdout)
    while len(dbusername) == 0:
        dbusername = messages.ask('Enter database username', file=sys.stdout)
    while len(dbpassword) == 0:
        dbpassword = messages.ask('Enter database password', secret=True, file=sys.stdout)

    if database.set_credentials(dbhost, dbport, dbname, dbusername, dbpassword):
        messages.success('Connected to database', file=sys.stdout)
    else:
        return

    # Display all DataFrame rows
    pd.set_option('display.max_rows', None)

    override_execution(allow_code_execution)


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
