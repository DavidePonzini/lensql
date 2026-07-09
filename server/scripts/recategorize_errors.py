import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import os
import sys

from dav_tools import database, messages, argument_parser
from sqlchecker import build_catalog, get_errors, detectors, DetectedError
from sqlscope import Catalog

from server.db.admin import Query, Dataset
from server.db.admin.connection import db, SCHEMA
from server.db.users import get_database

from tqdm import tqdm
NCOLS = 80


SerializedError = tuple[int, list[str]]

SYSTEM_CATALOGS: dict[str, Catalog] = {}

DETECTORS: list[type[detectors.BaseDetector]] = [
    detectors.SyntaxErrorDetector,
    # detectors.SemanticErrorDetector,
    # detectors.LogicalErrorDetector,
    # detectors.ComplicationDetector,
]

def detect_errors(query: Query) -> list[DetectedError]:
    context_columns, context_unique_constraints = query.get_context()

    dataset = Dataset(query.query_batch.exercise.dataset_id)

    user_catalog = build_catalog(
        columns_info=context_columns,
        unique_constraints_info=context_unique_constraints
    )
    # use SYSTEM_CATALOGS to cache system catalogs for each dbms type
    if dataset.dbms not in SYSTEM_CATALOGS:
        SYSTEM_CATALOGS[dataset.dbms] = get_database('lens', dataset.dbms).get_system_catalog()
    system_catalog = SYSTEM_CATALOGS[dataset.dbms]
    catalog = user_catalog.merge(system_catalog)

    return get_errors(
                    query_str=query.sql_string,
                    solutions=query.query_batch.exercise.solutions,
                    catalog=catalog,
                    search_path=query.search_path,
                    solution_search_path=dataset.search_path,
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

def log_errors(query_id: int, errors: list[SerializedError]) -> None:
    for error_id, details in errors:
        db.insert(SCHEMA, 'has_error', {
            'query_id': query_id,
            'error_id': error_id,
            'details': details
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

def process_query(query_id: int) -> tuple[int, int, list[SerializedError], str | None]:
    query = Query(query_id)

    try:
        old_count = len(query.errors)
        errors = detect_errors(query)
    except Exception as e:
        return query_id, 0, [], str(e)

    return query_id, old_count, [
        (error.error.value, [str(v) for v in error.data])
        for error in errors
    ], None

def recategorize_errors(query_ids: list[int], jobs: int) -> tuple[int, int]:
    old_count = 0
    new_count = 0

    if jobs <= 1:
        results = (process_query(query_id) for query_id in query_ids)
        iterator = tqdm(results, total=len(query_ids), dynamic_ncols=True)

        for query_id, query_old_count, errors, error in iterator:
            if error is not None:
                print(file=sys.stderr)
                messages.error(f'Error processing query {query_id}: {error}')
                continue

            old_count += query_old_count
            new_count += len(errors)

            query = Query(query_id)
            delete_existing_errors(query)
            log_errors(query_id, errors)
            iterator.set_postfix_str(f'errors: {(new_count - old_count):+d}')

        return old_count, new_count

    context = multiprocessing.get_context('spawn')
    with ProcessPoolExecutor(max_workers=jobs, mp_context=context) as executor:
        futures = [
            executor.submit(process_query, query_id)
            for query_id in query_ids
        ]


        with tqdm(as_completed(futures), total=len(futures), dynamic_ncols=True) as progress:
            for future in progress:
                query_id, query_old_count, errors, error = future.result()
                if error is not None:
                    print(file=sys.stderr)
                    messages.error(f'Error processing query {query_id}: {error}')
                    continue

                old_count += query_old_count
                new_count += len(errors)

                query = Query(query_id)
                delete_existing_errors(query)
                log_errors(query_id, errors)
                progress.set_postfix_str(f'errors: {(new_count - old_count):+d}')

    return old_count, new_count


if __name__ == '__main__':
    argument_parser.add_argument(
        '-j', '--jobs',
        type=int,
        default=os.cpu_count() or 1,
        help='number of worker processes to use'
    )

    argument_parser.parse_args()

    query_ids = [query.query_id for query in list_queries()]
    old_count, new_count = recategorize_errors(query_ids, argument_parser.args.jobs)

    messages.info(f'Detected {old_count} -> {new_count} errors total.')
    
