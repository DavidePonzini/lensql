from dav_tools import database, messages
from sql_error_categorizer import build_catalog, get_errors, detectors, DetectedError

from server.db.admin import Query
from server.db.admin.connection import db, SCHEMA

from tqdm import tqdm


DETECTORS = [
    detectors.SyntaxErrorDetector,
    detectors.SemanticErrorDetector,
    detectors.LogicalErrorDetector,
    detectors.ComplicationDetector,
]

def detect_errors(query: Query) -> list[DetectedError]:
    context_columns, context_unique_constraints = query.get_context()

    catalog = build_catalog(
        columns_info=context_columns,
        unique_constraints_info=context_unique_constraints
    )

    return get_errors(
                    query_str=query.sql_string,
                    solutions=query.query_batch.exercise.solutions,
                    catalog=catalog,
                    search_path=query.search_path,
                    solution_search_path=query.query_batch.exercise.search_path,
                    detectors=DETECTORS
                )

def delete_existing_errors(query: Query) -> None:
    delete_query = database.sql.SQL(
        '''
            DELETE FROM {schema}.has_error
            WHERE query_id = {query_id}
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA),
        query_id=database.sql.Placeholder('query_id')
    )

    db.execute(delete_query, {
        'query_id': query.query_id
    })

def list_queries() -> list[Query]:
    query = database.sql.SQL(
        '''
            SELECT id
            FROM {schema}.queries
            WHERE query_type = 'SELECT'
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA)
    )

    result = db.execute_and_fetch(query)

    return [Query(row[0]) for row in result]


if __name__ == '__main__':
    for query in tqdm(list_queries(), ncols=80):
        old_errors = query.errors
        errors = detect_errors(query)

        delete_existing_errors(query)
        query.log_errors(errors)