'''This file serves only to properly cast the return types of Iterable[0]'''

from typing import Iterable

from server.sql.result import QueryResult, QueryResultDataset
from server.sql import SQLCode


def next_result(results: Iterable[QueryResult]) -> QueryResultDataset:
    return next(results, None)

def next_statement(codes: Iterable[SQLCode]) -> SQLCode:
    return next(codes, None)