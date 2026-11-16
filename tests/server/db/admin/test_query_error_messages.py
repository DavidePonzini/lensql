from sqlchecker import DetectedError, SqlErrors
from server.db.admin.queries import Query


def test_log_errors_stores_explanation(mocker):
    insert = mocker.patch('server.db.admin.queries.db.insert')
    error = DetectedError(SqlErrors.UNDEFINED_COLUMN, data=('age',), message='The age column does not exist.')
    Query(42).log_errors([error])
    assert insert.call_args.args[2] == {
        'query_id': 42, 'error_id': error.error.value,
        'details': ['age'], 'message': error.message,
    }


def test_load_errors_preserves_message(mocker):
    mocker.patch('server.db.admin.queries.db.execute_and_fetch', return_value=[
        (4, ['age'], 'Saved explanation.'), (22, None, 'A semicolon is missing.'),
    ])
    errors = Query(42).errors
    assert errors[0].message == 'Saved explanation.'
    assert errors[0].data == ('age',)
    assert 'semicolon' in errors[1].message


def test_detect_errors_prompt_uses_message(app):
    from server.llm.prompts.query_result import detect_errors
    error = DetectedError(SqlErrors.UNDEFINED_COLUMN, data=('age',), message='The age column does not exist.')
    with app.test_request_context():
        prompt = detect_errors('SELECT age FROM people;', errors=[error])
    assert '- The age column does not exist.' in prompt
    assert 'UNDEFINED_COLUMN' not in prompt
