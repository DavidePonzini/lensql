
def explain_error(query: str, exception: Exception):
    return  f'''
I encountered an error while trying to execute the following SQL query. Please briefly explain what this error means.
Do not provide the correct answer, I only want an explanation of the error.

Format the response as follows:
- the error message should be enclosed in <b></b> tags
- SQL code (e.g. tables, columns or keywords) should be enclosed in <code></code> tags

-- SQL Query --
{query}

-- Error --
{exception}

-- Template answer --
The error <b>ERROR</b> means that EXPLANATION.
<br>
<br>
The error occurred because REASON.
<br>
<br>
<i>BRIEF MOTIVATIONALLY-POSITIVE MESSAGE.</i>
'''


def guide_user(query: str, exception: Exception):
    return f'''
I encountered an error while trying to execute the following SQL query. Please provide guidance on how to fix this error.
Do not provide the correct answer, I only want guidance on how to fix the error.

Format the response as follows:
- each step should be enclosed in <li></li> tags
- all steps should be enclosed in <ol></ol> tags
- SQL code (e.g. tables, columns or keywords) should be enclosed in <code></code> tags

-- SQL Query --
{query}

-- Error --
{exception}

-- Template answer --
To fix this error, you should follow these steps:
<ol>
    <li>First, you need to CHECK THIS.</li>
    <li>Next, you should TRY THAT.</li>
    <li>Finally, you can VERIFY THE RESULT.</li>
</ol>
<br>
<i>BRIEF MOTIVATIONALLY-POSITIVE MESSAGE.</i>
'''