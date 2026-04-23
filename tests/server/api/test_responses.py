from flask import Flask

from server.api.util import responses


class FakeReward:
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {'name': self.name}


class FakeQuery:
    def __init__(self):
        self.success = True
        self.query = type('QueryText', (), {'query': 'SELECT 1'})()
        self.data_type = 'dataset'
        self.result_html = '<table></table>'
        self.query_id = 42


def test_response_serializes_success_rewards_and_payload():
    app = Flask(__name__)

    with app.app_context():
        response = responses.response(
            True,
            rewards=[FakeReward('xp')],
            badges=[FakeReward('badge')],
            message='ok',
        )

    assert response.get_json() == {
        'success': True,
        'rewards': [{'name': 'xp'}],
        'badges': [{'name': 'badge'}],
        'message': 'ok',
    }


def test_response_query_serializes_query_payload():
    app = Flask(__name__)

    with app.app_context():
        response = responses.response_query(FakeQuery(), is_builtin=True)

    assert response.get_json() == [{
        'success': True,
        'builtin': True,
        'query': 'SELECT 1',
        'type': 'dataset',
        'data': '<table></table>',
        'id': 42,
        'rewards': [],
        'badges': [],
    }]


def test_streaming_response_uses_ndjson_content_type():
    response = responses.streaming_response(['{"success": true}\n'])

    assert response.content_type == 'application/x-ndjson'
