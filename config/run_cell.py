from dav_tools import messages
import psycopg2
from IPython.core.interactiveshell import ExecutionResult, ExecutionInfo

import webui
import pandas as pd

DB_NAME = None
DB_USERNAME = None
DB_PASSWORD = None
DB_ADDRESS = None

SQL_COMMANDS = ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'SET')


def run_cell(shell, raw_cell, **kwargs) -> ExecutionResult:
    '''Automatically executes SQL queries when detected in a Jupyter Notebook cell.'''

    if DB_ADDRESS is None or DB_USERNAME is None or DB_PASSWORD is None or DB_NAME is None:
        messages.error('Module not configured, please run the setup function first')
        return
    
    if not raw_cell.strip().upper().startswith(SQL_COMMANDS):
        return shell.run_cell_original(raw_cell, **kwargs)

    # execute SQL query
    try:
        conn = psycopg2.connect(user=DB_USERNAME, password=DB_PASSWORD, host=DB_ADDRESS, dbname=DB_NAME)
        cur = conn.cursor()
        cur.execute(raw_cell)
        conn.commit()
        
        if cur.description:  # Check if the query has a result set
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            result = pd.DataFrame(rows, columns=columns)
            
            webui.show_result(raw_cell, result)
        else:
            print(f'Affected rows: {cur.rowcount}')
            result = None

        return return_result(result, raw_cell, **kwargs)
    except Exception as e:
        webui.show_error(code=raw_cell, exception=e)
        return
    finally:
        cur.close()
        conn.close()

def return_result(result, raw_cell, store_history, silent, cell_id, shell_futures=True) -> ExecutionResult:
    res = ExecutionResult(ExecutionInfo(raw_cell, store_history, silent, shell_futures, cell_id))
    res.result = result

    return res

