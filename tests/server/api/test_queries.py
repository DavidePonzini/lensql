from types import SimpleNamespace

import pytest


def _fake_query_result(query_text):
    return SimpleNamespace(
        success=True,
        query=SimpleNamespace(query=query_text),
        data_type='message',
        result_html='ok',
        result_text='ok',
        query_id=None,
        notices=[],
    )


@pytest.mark.parametrize(
    ('path', 'database_method'),
    [
        ('/queries/builtin/show-search-path', 'builtin_show_search_path'),
        ('/queries/builtin/list-tables', 'builtin_list_tables'),
        ('/queries/builtin/list-constraints', 'builtin_list_constraints'),
    ],
)
def test_builtin_query_endpoints_use_database_and_log_results(authenticated_client, mocker, path, database_method):
    fake_user = SimpleNamespace(username='alice')
    fake_exercise = SimpleNamespace(dataset_id='dataset-1')
    fake_dataset = SimpleNamespace(dbms='postgresql')
    fake_result = _fake_query_result('BUILTIN_SQL')
    fake_database = SimpleNamespace(**{
        database_method: lambda: iter([fake_result]),
    })

    mock_user = mocker.patch('server.api.queries.db.admin.User', return_value=fake_user)
    mock_exercise = mocker.patch('server.api.queries.db.admin.Exercise', return_value=fake_exercise)
    mock_dataset_ctor = mocker.patch('server.api.queries.db.admin.Dataset', return_value=fake_dataset)
    mock_get_database = mocker.patch('server.api.queries.db.users.get_database', return_value=fake_database)
    mock_log_builtin_query = mocker.patch('server.api.queries.log_builtin_query', return_value=123)

    response = authenticated_client.post(path, json={'exercise_id': 7})

    assert response.status_code == 200
    assert response.get_json() == [{
        'success': True,
        'builtin': True,
        'query': 'BUILTIN_SQL',
        'type': 'message',
        'data': 'ok',
        'id': 123,
        'rewards': [],
        'badges': [],
    }]

    mock_user.assert_called_once_with('alice')
    mock_exercise.assert_called_once_with(7)
    mock_dataset_ctor.assert_called_once_with('dataset-1')
    mock_get_database.assert_called_once_with(dbname='alice', dbms='postgresql')
    mock_log_builtin_query.assert_called_once_with(fake_user, fake_exercise, fake_result)


def test_builtin_list_users_endpoint_returns_first_result_from_iterator(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')
    fake_exercise = SimpleNamespace(dataset_id='dataset-1')
    fake_dataset = SimpleNamespace(dbms='postgresql')
    first_result = _fake_query_result('FIRST')
    second_result = _fake_query_result('SECOND')
    fake_database = SimpleNamespace(
        builtin_list_users=lambda: iter([first_result, second_result]),
    )

    mocker.patch('server.api.queries.db.admin.User', return_value=fake_user)
    mocker.patch('server.api.queries.db.admin.Exercise', return_value=fake_exercise)
    mocker.patch('server.api.queries.db.admin.Dataset', return_value=fake_dataset)
    mocker.patch('server.api.queries.db.users.get_database', return_value=fake_database)
    mocker.patch('server.api.queries.log_builtin_query', return_value=999)

    response = authenticated_client.post('/queries/builtin/list-users', json={'exercise_id': 7})

    assert response.status_code == 200
    assert response.get_json()[0]['query'] == 'FIRST'
    assert response.get_json()[0]['id'] == 999
