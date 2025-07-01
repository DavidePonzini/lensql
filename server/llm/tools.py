import json
from .chatgpt import llm_tool, ToolParameter
from server import db

@llm_tool('Returns the current search path in the database. Useful for checking if the user is in the right place.')
def get_search_path(username: str) -> str:
    return db.users.queries.metadata.get_search_path(username)

@llm_tool('Returns a list of tables, along with their columns in the current database. Useful for checking if an object actually exists.')
def get_tables(username: str) -> str:
    columns = db.users.queries.metadata.get_columns(username)
    unique = db.users.queries.metadata.get_unique_columns(username)

    return json.dumps(columns) + '\n\n' + json.dumps(unique)