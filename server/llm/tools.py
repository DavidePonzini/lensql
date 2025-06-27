from .chatgpt import llm_tool

@llm_tool('Returns the current search path in the database.')
def get_search_path() -> str:
    return 'public'

@llm_tool('Returns a list of tables, along with their columns in the current database.')
def get_tables() -> str:
    return 'table1(id, name), table2(id), table3(stipendio, nome, cognome)'