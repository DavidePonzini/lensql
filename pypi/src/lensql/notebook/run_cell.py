from .. import webui

from .. import database

from dav_tools import messages
import psycopg2
from IPython.core.interactiveshell import ExecutionResult, ExecutionInfo
import pandas as pd

SQL_COMMANDS = ('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'SET')


def run_cell_sql_python(shell, raw_cell: str, **kwargs) -> ExecutionResult:
    '''Executes SQL queries when the cell starts with a SQL command. Otherwise, executes Python code.'''

    if not raw_cell.strip().upper().startswith(SQL_COMMANDS):
        return shell.run_cell_original(raw_cell, **kwargs)
    
    return run_cell_sql_only(shell, raw_cell, **kwargs)

def run_cell_sql_only(shell, raw_cell: str, **kwargs) -> ExecutionResult:
    '''Executes SQL queries.'''

    if not database.are_credentials_set():
        messages.error('Module not configured, please run the setup function first')
        return

    # execute SQL query
    try:
        conn = database.connect()
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

