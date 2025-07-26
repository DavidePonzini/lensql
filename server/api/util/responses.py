from typing import Iterable as _Iterable
from flask import jsonify as _jsonify, Response as _Response

from server import gamification
from server.sql import QueryResult as _QueryResult


def response(success: bool = True, rewards: list[gamification.Reward] = [], badges: list[gamification.Reward] = [], **kwargs) -> _Response:
    return _jsonify({
        'success': success,
        'rewards': [reward.to_dict() for reward in rewards],
        'badges': [badge.to_dict() for badge in badges],
        **kwargs
    })

def response_query(
        *results: _QueryResult,
        is_builtin: bool = False,
        rewards: list[gamification.Reward] = [],
        badges: list[gamification.Reward] = [],
        **kwargs) -> _Response:
    return _jsonify([
        {
            'success': query.success,
            'builtin': is_builtin,
            'query': query.query.query,
            'type': query.data_type,
            'data': query.result_html,
            'id': query.id,
            'rewards': [reward.to_dict() for reward in rewards],
            'badges': [badge.to_dict() for badge in badges],
            **kwargs
        }
        for query in results
    ])

def streaming_response(data: _Iterable[str]) -> _Response:
    return _Response(data, content_type='application/x-ndjson')

NOT_IMPLEMENTED = 'This feature is not implemented yet. Please check back later.'
