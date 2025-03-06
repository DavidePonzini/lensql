def explain_error(query: str, exception: Exception):
    return  f'''
I encountered an error while trying to execute the following SQL query. Please briefly explain what might be the cause of the error.

-- SQL Query --
{query}

-- Error --
{exception}
'''