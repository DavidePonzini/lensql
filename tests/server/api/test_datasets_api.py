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


def test_add_user_to_dataset_requires_admin(authenticated_client, mocker):
    '''Test that only admin users can add users to datasets.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=False)

    mocker.patch('server.api.datasets.db.admin.User', return_value=fake_admin_user)

    response = authenticated_client.post(
        '/datasets/add-user',
        json={'dataset_id': 'DS1', 'username': 'target_user', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is False
    assert 'permission' in response.get_json()['message'].lower()


def test_add_user_to_dataset_by_admin_success_as_participant(authenticated_client, mocker):
    '''Test admin can add a user as a participant to a dataset.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='target_user', exists=lambda: True)
    fake_dataset = mocker.Mock()
    fake_dataset.exists.return_value = True

    mocker.patch('server.api.datasets.db.admin.User', side_effect=[fake_admin_user, fake_target_user])
    mocker.patch('server.api.datasets.db.admin.Dataset', return_value=fake_dataset)

    response = authenticated_client.post(
        '/datasets/add-user',
        json={'dataset_id': 'DS1', 'username': 'target_user', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is True
    fake_dataset.add_participant.assert_called_once_with(fake_target_user)
    fake_dataset.set_owner_status.assert_called_once_with(fake_target_user, False)


def test_add_user_to_dataset_by_admin_success_as_owner(authenticated_client, mocker):
    '''Test admin can add a user as an owner to a dataset.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='target_user', exists=lambda: True)
    fake_dataset = mocker.Mock()
    fake_dataset.exists.return_value = True

    mocker.patch('server.api.datasets.db.admin.User', side_effect=[fake_admin_user, fake_target_user])
    mocker.patch('server.api.datasets.db.admin.Dataset', return_value=fake_dataset)

    response = authenticated_client.post(
        '/datasets/add-user',
        json={'dataset_id': 'DS1', 'username': 'target_user', 'is_owner': True},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is True
    fake_dataset.add_participant.assert_called_once_with(fake_target_user)
    fake_dataset.set_owner_status.assert_called_once_with(fake_target_user, True)


def test_add_user_to_dataset_dataset_not_found(authenticated_client, mocker):
    '''Test adding a user to a non-existent dataset fails.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='target_user')
    fake_dataset = mocker.Mock()
    fake_dataset.exists.return_value = False

    mocker.patch('server.api.datasets.db.admin.User', side_effect=[fake_admin_user, fake_target_user])
    mocker.patch('server.api.datasets.db.admin.Dataset', return_value=fake_dataset)

    response = authenticated_client.post(
        '/datasets/add-user',
        json={'dataset_id': 'NONEXISTENT', 'username': 'target_user', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is False
    assert 'does not exist' in response.get_json()['message'].lower()


def test_add_user_to_dataset_user_not_found(authenticated_client, mocker):
    '''Test adding a non-existent user to a dataset fails.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='nonexistent', exists=lambda: False)
    fake_dataset = mocker.Mock()
    fake_dataset.exists.return_value = True

    # Create a Mock object that tracks calls and returns appropriate values
    user_mock = mocker.Mock(side_effect=[fake_admin_user, fake_target_user])

    mocker.patch('server.api.datasets.db.admin.User', user_mock)
    mocker.patch('server.api.datasets.db.admin.Dataset', return_value=fake_dataset)

    response = authenticated_client.post(
        '/datasets/add-user',
        json={'dataset_id': 'DS1', 'username': 'nonexistent', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is False
    assert 'user does not exist' in response.get_json()['message'].lower()
