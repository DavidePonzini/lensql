def get_localized(values: dict[str, str], language: str) -> str:
    '''
    Returns the localized value for the given language, or the English value if the language is not found.
    '''

    result = values.get(language, values['it']).strip()

    from dav_tools import messages
    messages.debug(f'Localized value for language "{language}": {result}')
    
    return result

def build_prompt(request: dict[str, str], query: str, template: dict[str, str], language: str) -> str:
        return f'''
{request.get(language, request['en'])}

{RESPONSE_FORMAT.get(language, RESPONSE_FORMAT['en'])}

{SECTION_QUERY.get(language, SECTION_QUERY['en']).format(language=language)}
{query}

{SECTION_TEMPLATE.get(language, SECTION_TEMPLATE['en'])}
{template.get(language, template['en'])}
'''

##################################################################################################################
SECTION_QUERY = {
    'en': '-- {language} Query --',
    'it': '-- Query {language} --',
}

SECTION_TEMPLATE = {
    'en': '--- Answer Template --',
    'it': '--- Template di Risposta --',
}

SECTION_ERROR = {
    'en': '-- Error --',
    'it': '-- Errore --',
}

RESPONSE_FORMAT = {
    'en': '''
Format the response as follows:
- SQL code (e.g. tables, columns or keywords) should be enclosed in <code></code> tags
- Bold text should be enclosed in <b></b> tags
- You should refer to records/tuples/rows as rows
''',
    'it': '''
Formatta la risposta come segue:
- Il codice SQL (ad esempio tabelle, colonne o parole chiave) deve essere racchiuso tra i tag <code></code>
- Il testo in grassetto deve essere racchiuso tra i tag <b></b>
- Dovresti riferirti a record/tuple/righe come righe
''',
}
