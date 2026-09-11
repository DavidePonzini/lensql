import argparse
import sys

from dav_tools import argument_parser, database, messages
from tqdm import tqdm

from server.db.admin import Query
from server.db.admin.connection import SCHEMA, db
from server.sql.code import SQLCode


PRESERVED_GOALS = {'BUILTIN', 'CHECK_SOLUTION'}


def list_queries() -> list[tuple[int, str, str | None]]:
    statement = database.sql.SQL(
        '''
            SELECT id, query_type, query_goal
            FROM {schema}.queries
            ORDER BY id
        '''
    ).format(schema=database.sql.Identifier(SCHEMA))

    return [
        (int(query_id), query_type, query_goal)
        for query_id, query_type, query_goal in db.execute_and_fetch(statement)
    ]


def get_query_goal(query: Query, query_type: str, current_goal: str | None) -> str:
    '''Return the recalculated goal, retaining application-specific categories.'''

    if current_goal in PRESERVED_GOALS:
        return current_goal

    return SQLCode(query.sql_string, builtin=query_type == 'BUILTIN').query_goal


def update_query_goal(query_id: int, query_goal: str) -> None:
    statement = database.sql.SQL(
        '''
            UPDATE {schema}.queries
            SET query_goal = {query_goal}
            WHERE id = {query_id}
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA),
        query_goal=database.sql.Placeholder('query_goal'),
        query_id=database.sql.Placeholder('query_id'),
    )

    db.execute(statement, {'query_id': query_id, 'query_goal': query_goal})


def recategorize_goals(
    queries: list[tuple[int, str, str | None]], start: int | None, end: int | None
) -> int:
    query_ids = {query_id for query_id, _, _ in queries}

    if start is not None and start > max(query_ids, default=start):
        messages.error(f'Start query ID {start} is greater than the maximum query ID.')
        return 0
    if end is not None and end < min(query_ids, default=end):
        messages.error(f'End query ID {end} is less than the minimum query ID.')
        return 0

    queries = [
        query_info
        for query_info in queries
        if (start is None or query_info[0] >= start)
        and (end is None or query_info[0] <= end)
    ]

    changed_count = 0
    progress = tqdm(queries, dynamic_ncols=True)
    for query_id, query_type, current_goal in progress:
        try:
            query_goal = get_query_goal(Query(query_id), query_type, current_goal)
        except Exception as error:
            print(file=sys.stderr)
            messages.error(f'Error processing query {query_id}: {error}')
            continue

        if query_goal != current_goal:
            update_query_goal(query_id, query_goal)
            changed_count += 1

        progress.set_postfix_str(f'changed goals: {changed_count}')

    return changed_count


if __name__ == '__main__':
    argument_parser.add_argument(
        '-s', '--start', type=int, help='query ID to start from (inclusive)'
    )
    argument_parser.add_argument(
        '-e', '--end', type=int, help='query ID to end at (inclusive)'
    )
    argument_parser.parse_args()

    changed_count = recategorize_goals(
        queries=list_queries(),
        start=argument_parser.args.start,
        end=argument_parser.args.end,
    )
    messages.info(f'Recategorized query_goal for {changed_count} queries.')
