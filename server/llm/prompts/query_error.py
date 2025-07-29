from server.sql import SQLCode
from . import util

def explain_error(code: str, exception: str, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    return f'''
Hi Lens! I tried running the following {sql_language} query, but I ran into an error.
Could you please explain what this error means in simple terms?
You don't need to fix the query—just help me understand what's going wrong so I can learn from it.

{util.RESPONSE_FORMAT}

-- {sql_language} Query --
{query}

-- Error --
{exception}

-- Template answer --
The error <b>{exception}</b> means that EXPLANATION.
<br><br>
This usually occurs when REASON.
'''

def provide_error_example(code: str, exception: str, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    return f'''
Hi Lens! Could you please provide a simplified example of a {sql_language} query that would cause the same error as the one below?
The example should be extremely simplified, leaving out all query parts that do not contribute to generating the error message.
Remove conditions that are not necessary to reproduce the error.
You don't need to fix the query—just help me understand what kind of query would lead to this error.
Remember to use the <pre class="code m"> tag for the example query.

{util.RESPONSE_FORMAT}

-- {sql_language} Query --
{query}

-- Error --
{exception}

-- Template answer --
Let's see a similar query that BRIEF EXPLANATION OF THE ERROR CAUSE.
<pre class="code m">EXAMPLE QUERY</pre>
'''

def locate_error_cause(code: str, exception: str, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    return f'''
Hi Lens! I encountered an error while trying to execute the following {sql_language} query.
Could you please tell me which part of the query is likely causing the error?
You don't need to fix the query—just help me identify the problematic part so I can learn from it.

{util.RESPONSE_FORMAT}

-- {sql_language} Query --
{query}

-- Error --
{exception}

-- Template answer --
Let's look at the query and see which part of it is likely to have caused the error.
<pre class="code m">
WHOLE QUERY, WITH THE PART THAT CAUSES THE ERROR IN BOLD RED
</pre>
'''

def fix_query(code: str, exception: str, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    return f'''
Hey Lens, I can't figure out how to fix the following {sql_language} query.
Could you please provide a fixed version of the query that would not cause the same error as the one below?
You don't need to give me the whole query, just the part that needs to be changed. I will apply it to the original query.

{util.RESPONSE_FORMAT}

-- {sql_language} Query --
{query}

-- Error --
{exception}

-- Template answer --
To fix your query, you could try changing:
<pre class="code m'>ORIGINAL QUERY PART</pre>
to:
<pre class="code m">FIXED QUERY PART</pre>
'''
