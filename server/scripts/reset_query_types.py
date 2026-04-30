from dav_tools import database, messages

from server.db.admin import Query
from server.db.admin.connection import db, SCHEMA
from server.sql.code import SQLCode

from tqdm import tqdm


def list_queries() -> list[tuple[int, str, str]]:
    query = database.sql.SQL(
        '''
            SELECT id, query_type, query_goal
            FROM {schema}.queries
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA)
    )

    result = db.execute_and_fetch(query)
    return [(int(row[0]), row[1], row[2]) for row in result]


def reset_query_type(query: Query, current_query_type: str, query_goal: str) -> str:
    if current_query_type == 'BUILTIN' and query_goal == 'BUILTIN':
        return 'BUILTIN'
    else:
        new_query_type = SQLCode(query.sql_string).query_type

    update_query = database.sql.SQL(
        '''
            UPDATE {schema}.queries
            SET query_type = {query_type}
            WHERE id = {query_id}
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA),
        query_type=database.sql.Placeholder('query_type'),
        query_id=database.sql.Placeholder('query_id')
    )

    db.execute(update_query, {
        'query_type': new_query_type,
        'query_id': query.query_id,
    })

    return new_query_type


if __name__ == '__main__':
    changed_count = 0

    for query_id, old_query_type, query_goal in tqdm(list_queries(), ncols=80):
        query = Query(query_id)
        new_query_type = reset_query_type(query, old_query_type, query_goal)

        if new_query_type != old_query_type:
            changed_count += 1

    messages.info(f'Reset query_type for {changed_count} queries.')
