from server.sql import SQLCode
from . import util
import sqlscope

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

    def clause_template(clause: str, code: str) -> dict[str, str]:
        if clause == 'from':
            return {
                'en': f'The <code>FROM</code> clause (<code>{code}</code>) reads data from EXPLANATION OF FROM CLAUSE.',
                'it': f'La clausola <code>FROM</code> (<code>{code}</code>) legge i dati da SPIEGAZIONE DELLA CLAUSOLA FROM.',
            }
        if clause == 'where':
            return {
                'en': f'The <code>WHERE</code> clause (<code>{code}</code>) keeps only the rows EXPLANATION OF WHERE CLAUSE.',
                'it': f'La clausola <code>WHERE</code> (<code>{code}</code>) mantiene solo le righe SPIEGAZIONE DELLA CLAUSOLA WHERE.',
            }
        if clause == 'group_by':
            return {
                'en': f'The <code>GROUP BY</code> clause (<code>{code}</code>) groups the data EXPLANATION OF GROUP BY CLAUSE.',
                'it': f'La clausola <code>GROUP BY</code> (<code>{code}</code>) raggruppa i dati SPIEGAZIONE DELLA CLAUSOLA GROUP BY.',
            }
        if clause == 'having':
            return {
                'en': f'The <code>HAVING</code> clause (<code>{code}</code>) keeps only the groups EXPLANATION OF HAVING CLAUSE.',
                'it': f'La clausola <code>HAVING</code> (<code>{code}</code>) mantiene solo i gruppi SPIEGAZIONE DELLA CLAUSOLA HAVING.'
            }
        if clause == 'order_by':
            return {
                'en': f'The <code>ORDER BY</code> clause (<code>{code}</code>) sorts the results EXPLANATION OF ORDER BY CLAUSE.',
                'it': f'La clausola <code>ORDER BY</code> (<code>{code}</code>) ordina i risultati SPIEGAZIONE DELLA CLAUSOLA ORDER BY.',
            }
        if clause == 'limit':
            return {
                'en': f'The <code>LIMIT</code> clause (<code>{code}</code>) keeps only the first EXPLANATION OF LIMIT CLAUSE rows.',
                'it': f'La clausola <code>LIMIT</code> (<code>{code}</code>) mantiene solo le prime SPIEGAZIONE DELLA CLAUSOLA LIMIT righe.',
            }
        if clause == 'select':
            return {
                'en': f'The <code>SELECT</code> clause (<code>{code}</code>) makes the query return EXPLANATION OF SELECT CLAUSE.',
                'it': f'La clausola <code>SELECT</code> (<code>{code}</code>) fa sì che la query restituisca SPIEGAZIONE DELLA CLAUSOLA SELECT.',
            }
        return {
            'en': f'The <code>{code}</code> clause EXPLANATION OF {code} CLAUSE.',
            'it': f'La clausola <code>{code}</code> CLAUSE SPIEGAZIONE DELLA CLAUSOLA {code}.',
        }

    code = SQLCode(code).strip_comments().query

    query = sqlscope.Query(code)

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

    queries: list[dict] = []
    for select in query.selects:
        if not select.ast:
            # we can assume the AST is always valid, since this button can only be called after a successful execution of the query
            continue

        q: dict[str, str] = {
            'query': select.sql,
            'from': '',
            'where': '',
            'group_by': '',
            'having': '',
            'order_by': '',
            'limit': '',
            'offset': '',
            'select': '',
        }

        ast_args = select.ast.args

        if ast_args.get('from_'):
            q['from'] = ast_args["from_"].sql()
        if ast_args.get('joins'):
            q['from'] += ' ' + ' '.join(join.sql() for join in ast_args.get('joins', []))
        if ast_args.get('where'):
            q['where'] = ast_args['where'].sql()
        if ast_args.get('group'):
            q['group_by'] = ast_args['group'].sql()
        if ast_args.get('having'):
            q['having'] = ast_args['having'].sql()
        if ast_args.get('order'):
            q['order_by'] = ast_args['order'].sql()
        if ast_args.get('limit'):
            q['limit'] = ast_args['limit'].sql()
        if ast_args.get('offset'):
            q['offset'] = ast_args['offset'].sql()
        q['select'] = f'SELECT {", ".join(exp.sql() for exp in ast_args["expressions"])}'

        queries.append(q)

    # templates for each clause present in the query
    clauses_template = ''
    for q in queries:
        clauses_template += f'<li><code>{q["query"]}</code></li>'
        clauses_template += '<ol class="detailed-explanantion">'
        for clause in ['from', 'where', 'group_by', 'having', 'order_by', 'limit', 'offset', 'select']:
            if q[clause]:
                clauses_template += f'<li>{util.get_localized(clause_template(clause, q[clause]))}</li>'

        clauses_template += '</ol>'

    template = {
        'en': f'''
<div class="hidden">
The query you wrote <b>GOAL DESCRIPTION</b>.
<br><br>
</div>
Here is a detailed explanation of your query:
<ul>
{clauses_template}
</ul>
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