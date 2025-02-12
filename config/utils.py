from IPython.core.interactiveshell import ExecutionResult, ExecutionInfo


def return_result(shell, result, raw_cell, store_history, silent, shell_futures, cell_id):
    res = ExecutionResult(ExecutionInfo(raw_cell, store_history, silent, shell_futures, cell_id))
    res.result = result
    shell.displayhook(res.result)
    return res

def raise_exception(shell, e):
    shell.showtraceback((type(e), e, e.__traceback__))
