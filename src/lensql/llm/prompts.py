from ..sql import SQLCode

RESPONSE_FORMAT = '''
Format the response as follows:
- SQL code (e.g. tables, columns or keywords) should be enclosed in <code></code> tags
'''

MOTIVATIONAL_MESSAGE_RESULT = '''
BRIEF MOTIVATIONALLY-POSITIVE MESSAGE RELATED TO THE QUERY'S STYLE.
'''
MOTIVATIONAL_MESSAGE_ERROR = '''
BRIEF MOTIVATIONALLY-POSITIVE MESSAGE RELATED TO THE SPECIFIC ERROR ENCOUNTERED.
'''

def explain_error(code: str, exception: Exception, language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()
    
    return  f'''
I encountered an error while trying to execute the following {language} query. Please briefly explain what this error means.
Do not provide the correct answer, I only want an explanation of the error.

{RESPONSE_FORMAT}

-- SQL Query --
{query}

-- Error --
{exception}

-- Template answer --
The error <b>{exception}</b> means that EXPLANATION.
<br>
<br>
The error occurred because REASON.
<br>
<br>
<i>{MOTIVATIONAL_MESSAGE_ERROR}</i>
'''


def guide_user(code: str, exception: Exception, language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    return f'''
I encountered an error while trying to execute the following {language} query.
Please tell me which part of the query I should check to fix the error.
Do not correct the query, I only want guidance on where to look to fix the error.

{RESPONSE_FORMAT}

-- SQL Query --
{query}

-- Error --
{exception}

-- Template answer --
This error is caused by a problem in the following clause:
<pre class="code m">RELEVANT CODE</pre>
<br>
<i>{MOTIVATIONAL_MESSAGE_ERROR}</i>
'''


def explain_my_query(code: str, language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    clauses = [
        {
            'sql': 'FROM',
            'template': 'The <code>FROM</code> clause reads data from EXPLANATION OF FROM CLAUSE.'
        },
        {
            'sql': 'WHERE',
            'template': 'The <code>WHERE</code> clause keeps only the rows EXPLANATION OF WHERE CLAUSE.'
        },
        {
            'sql': 'GROUP BY',
            'template': 'The <code>GROUP BY</code> clause groups the data EXPLANATION OF GROUP BY CLAUSE.'
        },
        {
            'sql': 'HAVING',
            'template': 'The <code>HAVING</code> clause keeps only the groups EXPLANATION OF HAVING CLAUSE.'
        },
        {
            'sql': 'ORDER BY',
            'template': 'The <code>ORDER BY</code> clause sorts the results EXPLANATION OF ORDER BY CLAUSE.'
        },
        {
            'sql': 'LIMIT',
            'template': 'The <code>LIMIT</code> clause keeps only the first EXPLANATION OF LIMIT CLAUSE rows.'
        },
        {
            'sql': 'SELECT',
            'template': 'The <code>SELECT</code> clause makes the query return EXPLANATION OF SELECT CLAUSE.'
        }
    ]

    # keep only the clauses present in the query
    clauses = [clause for clause in clauses if query.has_clause(clause['sql'])]

    # templates for each clause present in the query
    templates = ''.join([f'<li>{clause["template"]}</li>' for clause in clauses])

    return f'''
Please explain the purpose of the following {language} query. What is the query trying to achieve?
Do not provide the correct answer and do not try to fix eventual errors, I only want an explanation of this query's purpose.
Assume the user has willingly formulated the query this way.

{RESPONSE_FORMAT}

-- SQL Query --
{query}

-- Template answer --
The query you wrote <b>GOAL DESCRIPTION</b>.
<br><br>
Here is a detailed explanation of the query:
<ol class="detailed-explanantion">
{templates}
</ol>
<br>
<i>{MOTIVATIONAL_MESSAGE_RESULT}</i>
'''
