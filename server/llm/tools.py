import json
from .chatgpt import llm_tool, ToolParameter
from server import db

@llm_tool('Returns the current search path in the database. Useful for checking if the user is in the right place.')
def get_search_path(username: str) -> str:
    return db.users.get_database('postgresql', username).get_search_path()

@llm_tool('Returns a list of tables, along with their columns and their properties, in the current database. Useful for checking what data is actually available.')
def get_tables(username: str) -> str:
    db_instance = db.users.get_database('postgresql', username)

    columns = [col.to_dict() for col in db_instance.get_columns()]
    unique = [col.to_dict() for col in db_instance.get_unique_columns()]

    return json.dumps(columns) + '\n\n' + json.dumps(unique)