from flask_babel import get_locale

def get_localized(values: dict[str, str]) -> str:
    '''
    Returns the localized value for the given language, or the English value if the language is not found.
    '''

    language = get_locale().language

    result = values.get(language, values['en']).strip()

    return result

##################################################################################################################
SECTION_QUERY = {
    'en': '-- {sql_language} Query --',
    'it': '-- Query {sql_language} --',
}

SECTION_TEMPLATE = {
    'en': '-- Answer Template --',
    'it': '-- Template di Risposta --',
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
