from typing import Iterable as _Iterable
from flask import jsonify as _jsonify, Response as _Response

from server.sql import QueryResult as _QueryResult


def response(success: bool = True, **kwargs) -> _Response:
    return _jsonify({
        'success': success,
        **kwargs
    })

def response_query(*results: _QueryResult, is_builtin: bool = False) -> _Response:
    return _jsonify([
        {
            'success': query.success,
            'builtin': is_builtin,
            'query': query.query,
            'type': query.query_type,
            'data': query.result,
            'id': query.id,
        }
        for query in results
    ])

def streaming_response(data: _Iterable[str]) -> _Response:
    return _Response(data, content_type='application/x-ndjson')

NOT_IMPLEMENTED = 'This feature is not implemented yet. Please check back later.'
