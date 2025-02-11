from IPython.core.interactiveshell import InteractiveShell, ExecutionResult, ExecutionInfo
import psycopg2
from IPython.core.compilerop import CachingCompiler
from IPython.utils.capture import capture_output

# Database connection parameters
DB_PARAMS = {
    "dbname": "postgres",
    "user": "jupyter_user",
    "password": "jupyter_pwd",  # Using your actual password
    "host": "localhost"
}

def return_result(self, result, raw_cell, store_history, silent, shell_futures, cell_id):
    res = ExecutionResult(ExecutionInfo(raw_cell, store_history, silent, shell_futures, cell_id))
    res.result = result
    self.displayhook(res.result)
    return res

def raise_exception(self, e):
    self.showtraceback((type(e), e, e.__traceback__))

def auto_execute_sql(self, raw_cell, store_history=True, silent=False, shell_futures=True, cell_id=None):
    """ Automatically executes SQL queries when detected in a Jupyter Notebook cell. """
    stripped_code = raw_cell.strip().lower()

    # SQL keywords to detect
    sql_keywords = ("select", "insert", "update", "delete", "create", "drop", "alter")

    # If it's not a SQL query, run it as normal code
    if not stripped_code.startswith(sql_keywords):
        return InteractiveShell.original_run_cell(self, raw_cell, store_history, silent, shell_futures, cell_id)

    # If it's not a SELECT query, don't run it
    if not stripped_code.startswith('select'):
        print('Query not executed, only SELECT is supported')
        return 

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute(raw_cell)
        rows = cur.fetchall()

        return return_result(self, rows, raw_cell, store_history, silent, shell_futures, cell_id)
    except Exception as e:
        raise_exception(self, e)
        return
    finally:
        cur.close()
        conn.close()

        
# Override Jupyter execution
InteractiveShell.original_run_cell = InteractiveShell.run_cell
InteractiveShell.run_cell = auto_execute_sql
