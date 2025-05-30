from server.sql import SQLCode
from server.db.admin.connection import db, SCHEMA
from tqdm import tqdm
from dav_tools import database

def categorize_all_queries():
    '''Categorize SQL queries by their type, if they are not already categorized.'''
    query = database.sql.SQL('''
        SELECT id, query
        FROM {schema}.queries
        WHERE query_type IS NULL
    ''').format(
        schema=database.sql.Identifier(SCHEMA)
    )

    result = db.execute_and_fetch(query)

    for row in tqdm(result, total=len(result)):
        query_id = row[0]
        query_text = row[1]

        sql_code = SQLCode(query_text)
        query_type = sql_code.query_type

        update_query = database.sql.SQL('''
            UPDATE {schema}.queries
            SET query_type = {query_type}
            WHERE id = {query_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            query_type=database.sql.Placeholder('query_type'),
            query_id=database.sql.Placeholder('query_id')
        )

        db.execute(update_query, {
            'query_type': query_type,
            'query_id': query_id
        })

if __name__ == '__main__':
    categorize_all_queries()
    