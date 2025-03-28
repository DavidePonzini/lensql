from . import chat

from .. import server

import pandas as pd
from IPython.display import display

def show_result(code: str, result: pd.DataFrame) -> None:
    display(result)

    query_id = server.log_query(query=code, success=True)
    chat.ResultChat(query_id, code, result).show()

def show_error(code: str, exception: Exception) -> None:
    query_id = server.log_query(query=code, success=False)
    chat.ErrorChat(query_id, code, exception).show()
