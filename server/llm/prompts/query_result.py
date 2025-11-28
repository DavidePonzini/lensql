from server.sql import SQLCode
from . import util

from sql_error_categorizer import DetectedError

def describe_my_query(code: str, *, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()

    request = {
        'en': f'''
Hi Lens! I would like to understand the purpose of the following {sql_language} query. What is it trying to achieve?
The query is not necessarily correct, so I don't need you to fix it. I just want to understand its goal.
Also, I know that the query has been deliberately formulated this way, so I don't need you to assume that it is a mistake or an error.
''',
        'it': f'''
Ciao Lens! Vorrei capire lo scopo della seguente query {sql_language}. Cosa sta cercando di ottenere?
La query non è necessariamente corretta, quindi non ho bisogno che tu la corregga. Voglio solo capire il suo obiettivo.
Inoltre, so che la query è stata formulata deliberatamente in questo modo, quindi non ho bisogno che tu assuma che ci sia un errore.
''',
    }

    template = {
        'en': '''
Let me see... it looks like your query <b>GOAL DESCRIPTION</b>.
''',
        'it': '''
Fammi vedere... sembra che la tua query <b>GOAL DESCRIPTION</b>.
''',
    }

    return f'''
{util.get_localized(request)}

{util.get_localized(util.RESPONSE_FORMAT)}

{util.get_localized(util.SECTION_QUERY).format(sql_language=sql_language)}
{query}

{util.get_localized(util.SECTION_TEMPLATE)}
{util.get_localized(template)}
'''

def explain_my_query(code: str, *, sql_language='PostgreSQL'):
    query = SQLCode(code)
    query = query.strip_comments()
    
    request = {
        'en': f'''
Hi Lens! I'm interested in diving deeper into the purpose of the following {sql_language} query.
Could you please explain what each part of the query does?
You don't need to fix the query—just help me understand its structure and purpose.
Also, I know that the query has been deliberately formulated this way, so I don't need you to assume that it is a mistake or an error.
''',
        'it': f'''
Ciao Lens! Sono interessato a esplorare più a fondo lo scopo della seguente query {sql_language}.
Potresti spiegarmi cosa fa ogni parte della query?
Non è necessario che tu corregga la query, voglio solo capire la sua struttura e il suo scopo.
Inoltre, so che la query è stata formulata deliberatamente in questo modo, quindi non ho bisogno che tu assuma che ci sia un errore.
''',
    }

    clauses = [
        {
            'sql': 'FROM',
            'template': {
                'en': 'The <code>FROM</code> clause reads data from EXPLANATION OF FROM CLAUSE.',
                'it': 'La clausola <code>FROM</code> legge i dati da SPIEGAZIONE DELLA CLAUSOLA FROM.',
            }
        },
        {
            'sql': 'WHERE',
            'template': {
                'en': 'The <code>WHERE</code> clause keeps only the rows EXPLANATION OF WHERE CLAUSE.',
                'it': 'La clausola <code>WHERE</code> mantiene solo le righe SPIEGAZIONE DELLA CLAUSOLA WHERE.',
            }
        },
        {
            'sql': 'GROUP BY',
            'template': {
                'en': 'The <code>GROUP BY</code> clause groups the data EXPLANATION OF GROUP BY CLAUSE.',
                'it': 'La clausola <code>GROUP BY</code> raggruppa i dati SPIEGAZIONE DELLA CLAUSOLA GROUP BY.',
            }
        },
        {
            'sql': 'HAVING',
            'template': {
                'en': 'The <code>HAVING</code> clause keeps only the groups EXPLANATION OF HAVING CLAUSE.',
                'it': 'La clausola <code>HAVING</code> mantiene solo i gruppi SPIEGAZIONE DELLA CLAUSOLA HAVING.'
            }
        },
        {
            'sql': 'ORDER BY',
            'template': {
                'en': 'The <code>ORDER BY</code> clause sorts the results EXPLANATION OF ORDER BY CLAUSE.',
                'it': 'La clausola <code>ORDER BY</code> ordina i risultati SPIEGAZIONE DELLA CLAUSOLA ORDER BY.',
            }
        },
        {
            'sql': 'LIMIT',
            'template': {
                'en': 'The <code>LIMIT</code> clause keeps only the first EXPLANATION OF LIMIT CLAUSE rows.',
                'it': 'La clausola <code>LIMIT</code> mantiene solo le prime SPIEGAZIONE DELLA CLAUSOLA LIMIT righe.',
            }
        },
        {
            'sql': 'SELECT',
            'template': {
                'en': 'The <code>SELECT</code> clause makes the query return EXPLANATION OF SELECT CLAUSE.',
                'it': 'La clausola <code>SELECT</code> fa sì che la query restituisca SPIEGAZIONE DELLA CLAUSOLA SELECT.',
            }
        },
    ]

    # keep only the clauses present in the query
    clauses = [clause for clause in clauses if query.has_clause(clause['sql'])]


    # templates for each clause present in the query
    clauses_template_values = []
    for clause in clauses:
        clauses_template_values.append(util.get_localized(clause['template']))
    clauses_template = ''.join([f'<li>{clause}</li>' for clause in clauses_template_values])

    template = {
        'en': f'''
<div class="hidden">
The query you wrote <b>GOAL DESCRIPTION</b>.
<br><br>
</div>
Here is a detailed explanation of your query:
<ol class="detailed-explanantion">
{clauses_template}
</ol>
''',
        'it': f'''
<div class="hidden">
La query che hai scritto <b>DESCRIZIONE OBIETTIVO</b>.
<br><br>
</div>
Ecco una spiegazione dettagliata della tua query:
<ol class="detailed-explanantion">
{clauses_template}
</ol>
''',
    }

    return f'''
{util.get_localized(request)}

{util.get_localized(util.RESPONSE_FORMAT)}

{util.get_localized(util.SECTION_QUERY).format(sql_language=sql_language)}
{query}

{util.get_localized(util.SECTION_TEMPLATE)}
{util.get_localized(template)}
'''

def detect_errors(code: str, *, sql_language='PostgreSQL', errors: list[DetectedError]=[]):
    query = SQLCode(code)
    query = query.strip_comments()

    request = {
        'en': f'''
Hi Lens! I'm wondering if my query has any mistakes or errors.
Could you please review the following {sql_language} query and provide a pedagogical student-oriented explanation to let me know if there are any issues with it.
If you find any mistakes, please explain what they are but don't fix them—I just want to understand if there are any problems.
I know that the query managed to execute successfully, but I want to make sure there are no hidden issues.
You'll be provided with a list of detected errors to help you in your analysis.
Don't use the error names in your explanation, just a description of the problem for each error.
''',
        'it': f'''
Ciao Lens! Mi chiedo se la mia query abbia degli errori o degli sbagli.
Potresti esaminare la seguente query {sql_language} e farmi sapere se ci sono dei problemi?
Se trovi degli errori, spiegami quali sono ma non correggerli—voglio solo capire se ci sono dei problemi.
So che la query è stata eseguita con successo, ma voglio assicurarmi che non ci siano problemi nascosti.
Ti verrà fornita una lista di errori rilevati per aiutarti nella tua analisi.
Non usare i nomi degli errori nella tua spiegazione, solo una descrizione del problema per ogni errore.
''',
    }

    template = {
        'en': '''
After reviewing your query, I found the following issues:
<ul>
<li>ERROR LIST ITEMS WITH EXPLANATIONS </li>
</ul>
''',
        'it': '''
Dopo aver esaminato la tua query, ho trovato i seguenti problemi:
<ul>
<li>ELEMENTI DELLA LISTA DEGLI ERRORI CON SPIEGAZIONI</li>
</ul>
''',
    }

    errors_str = '\n'.join([f'- {str(error)}' for error in errors])

    return f'''
{util.get_localized(request)}

{util.get_localized(util.RESPONSE_FORMAT)}

{util.get_localized(util.SECTION_DETECTED_ERRORS)}
{errors_str}

{util.get_localized(util.SECTION_QUERY).format(sql_language=sql_language)}
{query}

{util.get_localized(util.SECTION_TEMPLATE)}
{util.get_localized(template)}
'''