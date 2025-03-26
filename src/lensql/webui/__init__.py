from . import chat
from . import logger

import pandas as pd
from IPython.display import display

def show_result(code: str, result: pd.DataFrame) -> None:
    display(result)

    logger.log_query(code, True)

    chat.ResultChat(code, result).show()

def show_error(code: str, exception: Exception) -> None:
    logger.log_query(code, False)
    
    chat.ErrorChat(code, exception).show()
