from . import chat

from .. import server

import pandas as pd
from IPython.display import display

def show_result(code: str, result: pd.DataFrame) -> None:
    display(result)

    server.log_query(query=code, success=True)

    chat.ResultChat(code, result).show()

def show_error(code: str, exception: Exception) -> None:
    
    server.log_query(query=code, success=False)

    chat.ErrorChat(code, exception).show()
