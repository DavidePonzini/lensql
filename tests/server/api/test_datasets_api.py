import json
from types import SimpleNamespace


def test_export_dataset_returns_dump_for_owner(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')
    fake_dataset = SimpleNamespace(
        has_owner=lambda user: user.username == 'alice',
        dump=lambda: SimpleNamespace(dataset_id='DS1', title='Exported'),
    )

    mocker.patch('server.api.datasets.db.admin.User', return_value=fake_user)
    mocker.patch('server.api.datasets.db.admin.Dataset', return_value=fake_dataset)
    mock_asdict = mocker.patch(
        'server.api.datasets.asdict',
        return_value={'dataset_id': 'DS1', 'title': 'Exported'},
    )

    response = authenticated_client.get('/datasets/export/DS1')

    assert response.status_code == 200
    assert response.get_json() == {
        'success': True,
        'rewards': [],
        'badges': [],
        'data': {'dataset_id': 'DS1', 'title': 'Exported'},
    }
    mock_asdict.assert_called_once()


def test_import_dataset_loads_payload_and_assigns_current_user(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')
    fake_dataset = mocker.Mock()
    fake_dataset.dataset_id = 'NEW1'

    mocker.patch('server.api.datasets.db.admin.User', return_value=fake_user)
    mock_load_json = mocker.patch('server.api.datasets.db.admin.Dataset.load_json', return_value=fake_dataset)

    payload = json.dumps({'dataset_id': 'OLD1', 'title': 'Imported'})
    response = authenticated_client.post('/datasets/import', json={'payload': payload})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': True,
        'rewards': [],
        'badges': [],
        'dataset_id': 'NEW1',
    }
    mock_load_json.assert_called_once_with(payload)
    fake_dataset.add_participant.assert_called_once_with(fake_user)
    fake_dataset.set_owner_status.assert_called_once_with(fake_user, True)


def test_import_dataset_returns_error_for_invalid_json_payload(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')

    mocker.patch('server.api.datasets.db.admin.User', return_value=fake_user)
    mocker.patch(
        'server.api.datasets.db.admin.Dataset.load_json',
        side_effect=json.JSONDecodeError('Expecting value', '}', 0),
    )

    response = authenticated_client.post('/datasets/import', json={'payload': '}'})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': False,
        'rewards': [],
        'badges': [],
        'message': 'Failed to import dataset. JSON syntax error at line 1, column 1: Expecting value.',
    }


def test_import_dataset_returns_error_for_missing_field(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')

    mocker.patch('server.api.datasets.db.admin.User', return_value=fake_user)
    mocker.patch(
        'server.api.datasets.db.admin.Dataset.load_json',
        side_effect=KeyError('title'),
    )

    response = authenticated_client.post('/datasets/import', json={'payload': '{}'})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': False,
        'rewards': [],
        'badges': [],
        'message': 'Failed to import dataset. Missing required field: title.',
    }


def test_import_dataset_returns_error_for_server_failure(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')

    mocker.patch('server.api.datasets.db.admin.User', return_value=fake_user)
    mocker.patch(
        'server.api.datasets.db.admin.Dataset.load_json',
        side_effect=RuntimeError('db failed'),
    )

    response = authenticated_client.post('/datasets/import', json={'payload': '{}'})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': False,
        'rewards': [],
        'badges': [],
        'message': 'Failed to import dataset because the server encountered an error.',
    }
