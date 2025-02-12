import sys
from IPython.core.interactiveshell import InteractiveShell
from dav_tools import messages
import psycopg2

import utils
import pandas as pd

DB_PARAMS = None


def auto_execute_sql(shell, raw_cell, store_history=True, silent=False, shell_futures=True, cell_id=None):
    '''Automatically executes SQL queries when detected in a Jupyter Notebook cell.'''

    if DB_PARAMS is None:
        messages.error('Module not configured, please run the setup function first')
        return


    # If it's not a SQL query, run it as normal code
    stripped_code = raw_cell.strip().lower()
    sql_keywords = ('select', 'insert', 'update', 'delete', 'create', 'drop', 'alter', 'set', 'truncate', 'grant', 'revoke')
    if not stripped_code.startswith(sql_keywords):
        return InteractiveShell.original_run_cell(shell, raw_cell, store_history, silent, shell_futures, cell_id)

    # We have a SQL query, let's execute it
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute(raw_cell)
        conn.commit()
        
        if cur.description:  # Check if the query has a result set
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            df = pd.DataFrame(rows, columns=columns)
            result = df
        else:
            print(f'Affected rows: {cur.rowcount}')
            result = None

        return utils.return_result(shell, result, raw_cell, store_history, silent, shell_futures, cell_id)
    except Exception as e:
        utils.raise_exception(shell, e)
        return
    finally:
        cur.close()
        conn.close()