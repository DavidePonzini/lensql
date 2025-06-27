from server.sql import SQLCode
from . import util

def describe_my_query(code: str, language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    return f'''
Hi Lens! I would like to understand the purpose of the following {language} query. What is it trying to achieve?
The query is not necessarily correct, so I don't need you to fix it. I just want to understand its goal.
Also, I know that the query has been deliberately formulated this way, so I don't need you to assume that it is a mistake or an error.

{util.RESPONSE_FORMAT}

-- {language} Query --
{query}

-- Template answer --
Let me see... it looks like your query <b>GOAL DESCRIPTION</b>.
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
Hi Lens! I'm interested in diving deeper into the purpose of the following {language} query.
Could you please explain what each part of the query does?
You don't need to fix the query—just help me understand its structure and purpose.
Also, I know that the query has been deliberately formulated this way, so I don't need you to assume that it is a mistake or an error.

{util.RESPONSE_FORMAT}

-- {language} Query --
{query}

-- Template answer --
<div class="hidden">
The query you wrote <b>GOAL DESCRIPTION</b>.
<br><br>
</div>
Here is a detailed explanation of your query:
<ol class="detailed-explanantion">
{templates}
</ol>
'''
