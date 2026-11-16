from server.sql import SQLCode
from sqlchecker import DetectedError, SqlErrors
from . import util

def explain_error(code: str, exception: str, *, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    request = {
        'en': f'''
Hi Lens! I tried running the following {sql_language} query, but I ran into an error.
Could you please explain what this error means in simple terms?
You don't need to fix the query—just help me understand what's going wrong so I can learn from it.
''',
        'it': f'''
Ciao Lens! Ho provato a eseguire la seguente query {sql_language}, ma ho riscontrato un errore.
Potresti spiegarmi cosa significa questo errore in termini semplici?
Non è necessario che tu corregga la query, voglio solo capire cosa sta andando storto in modo da poter imparare da questo errore.
''',
    }

    template = {
        'en': '''
The error <b>{exception}</b> means that EXPLANATION.
<br><br>
This is occurring because REASON.
''',
        'it': '''
L'errore <b>{exception}</b> significa che SPIEGAZIONE.
<br><br>
Questo si verifica perché RAGIONE.
''',
    }

    return f'''
{util.get_localized(request)}

{util.get_localized(util.RESPONSE_FORMAT)}

{util.get_localized(util.SECTION_QUERY).format(sql_language=sql_language)}
{query}

{util.get_localized(util.SECTION_ERROR)}
{exception}

{util.get_localized(util.SECTION_TEMPLATE)}
{util.get_localized(template)}
'''

def provide_error_example(code: str, exception: str, *, sql_language='PostgreSQL'):
    # query = SQLCode(code)
    # query = query.strip_comments()

    request = {
        'en': f'''
Hi Lens! Could you please provide a simplified example of a {sql_language} query that would cause the same error as the one below?
The example should be extremely simplified, leaving out all query parts that do not contribute to generating the error message.
Remove conditions that are not necessary to reproduce the error.
You don't need to fix the query—just help me understand what kind of query would lead to this error.
Remember to use the <pre class="code m"> tag for the example query.
''',
        'it': f'''
Ciao Lens! Potresti fornire un esempio semplificato di una query {sql_language} che causerebbe lo stesso errore di seguito?
L'esempio dovrebbe essere estremamente semplificato, escludendo tutte le parti della query che non contribuiscono a generare il messaggio di errore.
Rimuovi le condizioni che non sono necessarie per riprodurre l'errore.
Non è necessario che tu corregga la query, voglio solo capire che tipo di query porterebbe a questo errore.
Ricorda di utilizzare il tag <pre class="code m"> per la query di esempio.
'''
    }

    template = {
        'en': '''
Let's see a similar query that BRIEF EXPLANATION OF THE ERROR CAUSE.
<pre class="code m">EXAMPLE QUERY</pre>
        ''',
        'it': '''
Vediamo una query simile che SPIEGAZIONE BREVE DELLA CAUSA DELL'ERRORE.
<pre class="code m">QUERY DI ESEMPIO</pre>
''',
    }

    return f'''
{util.get_localized(request)}

{util.get_localized(util.RESPONSE_FORMAT)}

{util.get_localized(util.SECTION_ERROR)}
{exception}

{util.get_localized(util.SECTION_TEMPLATE)}
{util.get_localized(template)}
'''

def locate_error_cause(code: str, exception: str, *, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    request = {
        'en': f'''
Hi Lens! I encountered an error while trying to execute the following {sql_language} query.
Could you please tell me which part of the query is likely causing the error?
You don't need to fix the query—just help me identify the problematic part so I can learn from it.
''',
        'it': f'''
Ciao Lens! Ho riscontrato un errore durante l'esecuzione della seguente query {sql_language}.
Potresti dirmi quale parte della query sta probabilmente causando l'errore?
Non è necessario che tu corregga la query, voglio solo identificare la parte problematica in modo da poter imparare da essa.
''',
    }

    template = {
        'en': '''
Let's look at the query... I see, the error is caused by this part here.
<pre class="code m">ONLY THE PART OF THE QUERY CAUSING THE ERROR</pre>
You might want to check if THIS PART is correct.
''',
        'it': '''
Diamo un'occhiata alla query... Capisco, l'errore è causato da questa parte qui.
<pre class="code m">SOLO LA PARTE DELLA QUERY CHE CAUSA L'ERRORE</pre>
Potresti voler controllare se QUESTA PARTE è corretta.
''',
    }

    return f'''
{util.get_localized(request)}

{util.get_localized(util.RESPONSE_FORMAT)}

{util.get_localized(util.SECTION_QUERY).format(sql_language=sql_language)}
{query}

{util.get_localized(util.SECTION_ERROR)}
{exception}

{util.get_localized(util.SECTION_TEMPLATE)}
{util.get_localized(template)}
'''

def fix_query(code: str, exception: str, *, sql_language='PostgreSQL', errors: list[DetectedError]=[]):
    query = SQLCode(code)
    query = query.strip_comments()

    error_hints = []
    for error in errors:
        if error.error in (
            SqlErrors.OMITTING_CORRELATION_NAMES,
            SqlErrors.AMBIGUOUS_COLUMN,
            SqlErrors.AMBIGUOUS_FUNCTION,
            SqlErrors.UNDEFINED_COLUMN,
            SqlErrors.UNDEFINED_FUNCTION,
            SqlErrors.UNDEFINED_PARAMETER,
            SqlErrors.UNDEFINED_OBJECT,
            SqlErrors.INVALID_SCHEMA_NAME,
            SqlErrors.MISSPELLINGS,
            SqlErrors.SYNONYMS,
            SqlErrors.OMITTED_QUOTES,
            SqlErrors.FAILURE_TO_SPECIFY_COLUMN_NAME_TWICE,
            SqlErrors.DATA_TYPE_MISMATCH,
            SqlErrors.AGGREGATE_FUNCTION_OUTSIDE_SELECT_OR_HAVING,
            SqlErrors.AGGREGATE_FUNCTIONS_CANNOT_BE_NESTED,
            SqlErrors.EXTRANEOUS_OR_OMITTED_GROUPING_COLUMN,
            SqlErrors.HAVING_WITHOUT_GROUP_BY,
            SqlErrors.CONFUSING_FUNCTION_WITH_FUNCTION_PARAMETER,
            SqlErrors.USING_WHERE_TWICE,
            SqlErrors.OMITTED_FROM_CLAUSE,
            SqlErrors.COMPARISON_WITH_NULL,
            SqlErrors.OMITTED_SEMICOLON,
            SqlErrors.DATE_TIME_FIELD_OVERFLOW,
            SqlErrors.DUPLICATE_CLAUSE,
            SqlErrors.UNDEFINED_CORRELATION_NAME,
            SqlErrors.TOO_MANY_COLUMNS_IN_SUBQUERY,
            SqlErrors.CONFUSED_TABLE_NAMES_WITH_COLUMN_NAMES,
            SqlErrors.RESTRICTION_IN_SELECT_CLAUSE,
            SqlErrors.PROJECTION_IN_WHERE_CLAUSE,
            SqlErrors.CONFUSED_ORDER_OF_KEYWORDS,
            SqlErrors.CONFUSED_LOGIC_OF_KEYWORDS,
            SqlErrors.CONFUSED_SYNTAX_OF_KEYWORDS,
            SqlErrors.OMITTED_COMMAS,
            SqlErrors.CURLY_OR_SQUARE_BRACKETS,
            SqlErrors.UNMATCHED_BRACKETS,
            SqlErrors.IS_WHERE_NOT_APPLICABLE,
            SqlErrors.NONSTANDARD_KEYWORDS_OR_STANDARD_KEYWORDS_IN_WRONG_CONTEXT,
            SqlErrors.NONSTANDARD_OPERATORS,
            SqlErrors.ADDITIONAL_SEMICOLON,
        ):
            error_hints.append(f'- {str(error)}')

    error_hints_str = '\n'.join(error_hints)

    request = {
        'en': f'''
Hey Lens, I can't figure out how to fix the following {sql_language} query.
Could you please provide a fixed version of the query that would not cause the same error as the one below?
You don't need to give me the whole query, just the part that needs to be changed. I will apply it myself to the original query.
''',
        'it': f'''
Ciao Lens, non riesco a capire come correggere la seguente query {sql_language}.
Potresti fornirmi una versione corretta della query che non causerebbe lo stesso errore di quella di seguito?
Non è necessario che tu mi dia l'intera query, solo la parte che deve essere modificata. La applicherò io stesso alla query originale.
''',
    }

    template = {
        'en': '''
To fix your query, you could try changing:
<pre class="code m">ORIGINAL QUERY PART</pre>
to:
<pre class="code m">FIXED QUERY PART</pre>
In this way, EXPLANATION OF THE FIX.
''',
        'it': '''
Per correggere la tua query, potresti provare a cambiare:
<pre class="code m">PARTE ORIGINALE DELLA QUERY</pre>
in:
<pre class="code m">PARTE CORRETTA DELLA QUERY</pre>
In questo modo, SPIEGAZIONE DELLA CORREZIONE.
''',
    }

    return f'''
{util.get_localized(request)}

{util.get_localized(util.RESPONSE_FORMAT)}

{util.get_localized(util.SECTION_DETECTED_ERRORS) if error_hints else ''}
{error_hints_str if error_hints else ''}

{util.get_localized(util.SECTION_QUERY).format(sql_language=sql_language)}
{query}

{util.get_localized(util.SECTION_ERROR)}
{exception}

{util.get_localized(util.SECTION_TEMPLATE)}
{util.get_localized(template)}
'''
