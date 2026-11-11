import json
import pytest
from psycopg2.errors import UniqueViolation
from datetime import datetime, timezone
from types import SimpleNamespace

from sqlscope import Dialect


def test_rename_activity_id_requires_admin(authenticated_client, mocker):
    mocker.patch('server.api.activities.db.admin.User', return_value=SimpleNamespace(is_admin=False))
    activity = mocker.patch('server.api.activities.db.admin.Activity')
    response = authenticated_client.post('/activities/rename-id', json={'activity_id': 'DS1', 'new_activity_id': 'DS2'})
    assert response.get_json()['success'] is False
    activity.assert_not_called()


def test_admin_can_rename_any_activity(authenticated_client, mocker):
    mocker.patch('server.api.activities.db.admin.User', return_value=SimpleNamespace(is_admin=True))
    activity = mocker.Mock()
    activity.rename_id.return_value = True
    factory = mocker.patch('server.api.activities.db.admin.Activity', return_value=activity)
    response = authenticated_client.post('/activities/rename-id', json={'activity_id': ' special-old ', 'new_activity_id': ' special-new '})
    assert response.get_json()['success'] is True
    assert response.get_json()['activity_id'] == 'SPECIAL-NEW'
    factory.assert_called_once_with('special-old')
    activity.rename_id.assert_called_once_with('SPECIAL-NEW')
    activity.has_owner.assert_not_called()
    activity.has_participant.assert_not_called()


@pytest.mark.parametrize('new_id', ['', ' ', None, 123, 'a/b', 'a?b', 'a#b', 'a b', '..'])
def test_rename_activity_rejects_invalid_id(authenticated_client, mocker, new_id):
    mocker.patch('server.api.activities.db.admin.User', return_value=SimpleNamespace(is_admin=True))
    activity = mocker.patch('server.api.activities.db.admin.Activity')
    response = authenticated_client.post('/activities/rename-id', json={'activity_id': 'DS1', 'new_activity_id': new_id})
    assert response.get_json()['success'] is False
    activity.assert_not_called()


@pytest.mark.parametrize('outcome, message', [(False, 'does not exist'), (UniqueViolation(), 'already in use')])
def test_rename_activity_handles_missing_and_duplicate_ids(authenticated_client, mocker, outcome, message):
    mocker.patch('server.api.activities.db.admin.User', return_value=SimpleNamespace(is_admin=True))
    activity = mocker.Mock()
    if isinstance(outcome, Exception):
        activity.rename_id.side_effect = outcome
    else:
        activity.rename_id.return_value = outcome
    mocker.patch('server.api.activities.db.admin.Activity', return_value=activity)
    response = authenticated_client.post('/activities/rename-id', json={'activity_id': 'DS1', 'new_activity_id': 'DS2'})
    assert response.get_json()['success'] is False
    assert message in response.get_json()['message']


def test_get_activity_exposes_activity_dates_to_teachers_only(authenticated_client, mocker):
    teacher = SimpleNamespace(username='alice', is_teacher=True)
    activity = SimpleNamespace(
        exists=lambda: True,
        has_participant=lambda user: True,
        name='Activity',
        description='Description',
        activity_str='SELECT 1;',
        search_path='public',
        dbms=Dialect.POSTGRES,
        activity_start_ts=datetime(2026, 10, 1, 9, tzinfo=timezone.utc),
        activity_end_ts=datetime(2026, 10, 1, 11, tzinfo=timezone.utc),
    )
    mocker.patch('server.api.activities.db.admin.User', return_value=teacher)
    mocker.patch('server.api.activities.db.admin.Activity', return_value=activity)

    response = authenticated_client.get('/activities/get/DS1')

    assert response.get_json()['data']['activity_start_ts'] == '2026-10-01T09:00:00+00:00'
    assert response.get_json()['data']['activity_end_ts'] == '2026-10-01T11:00:00+00:00'

    teacher.is_teacher = False
    response = authenticated_client.get('/activities/get/DS1')
    assert 'activity_start_ts' not in response.get_json()['data']
    assert 'activity_end_ts' not in response.get_json()['data']


def test_update_activity_persists_activity_dates_for_teacher(authenticated_client, mocker):
    teacher = SimpleNamespace(username='alice', is_teacher=True)
    activity = mocker.Mock()
    activity.has_owner.return_value = True
    mocker.patch('server.api.activities.db.admin.User', return_value=teacher)
    mocker.patch('server.api.activities.db.admin.Activity', return_value=activity)

    response = authenticated_client.put('/activities', json={
        'activity_id': 'DS1',
        'title': 'Activity',
        'description': '',
        'activity': '',
        'search_path': 'public',
        'dbms': 'postgres',
        'activity_start_ts': '2026-10-01T09:00',
        'activity_end_ts': '',
    })

    assert response.get_json()['success'] is True
    assert activity.update.call_args.kwargs['activity_start_ts'] == datetime(2026, 10, 1, 9, tzinfo=timezone.utc)
    assert activity.update.call_args.kwargs['activity_end_ts'] is None


def test_student_cannot_update_activity_dates(authenticated_client, mocker):
    student = SimpleNamespace(username='alice', is_teacher=False)
    activity = mocker.Mock()
    activity.has_owner.return_value = True
    mocker.patch('server.api.activities.db.admin.User', return_value=student)
    mocker.patch('server.api.activities.db.admin.Activity', return_value=activity)

    response = authenticated_client.put('/activities', json={
        'activity_id': 'DS1',
        'title': 'Activity',
        'description': '',
        'activity': '',
        'search_path': 'public',
        'dbms': 'postgres',
        'activity_start_ts': '2026-10-01T09:00',
    })

    assert response.get_json()['success'] is False
    activity.update.assert_not_called()


def test_export_activity_returns_dump_for_owner(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')
    fake_activity = SimpleNamespace(
        has_owner=lambda user: user.username == 'alice',
        dump=lambda: SimpleNamespace(activity_id='DS1', title='Exported'),
    )

    mocker.patch('server.api.activities.db.admin.User', return_value=fake_user)
    mocker.patch('server.api.activities.db.admin.Activity', return_value=fake_activity)
    mock_asdict = mocker.patch(
        'server.api.activities.asdict',
        return_value={'activity_id': 'DS1', 'title': 'Exported'},
    )

    response = authenticated_client.get('/activities/export/DS1')

    assert response.status_code == 200
    assert response.get_json() == {
        'success': True,
        'rewards': [],
        'badges': [],
        'data': {'activity_id': 'DS1', 'title': 'Exported'},
    }
    mock_asdict.assert_called_once()


def test_import_activity_loads_payload_and_assigns_current_user(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')
    fake_activity = mocker.Mock()
    fake_activity.activity_id = 'NEW1'

    mocker.patch('server.api.activities.db.admin.User', return_value=fake_user)
    mock_load_json = mocker.patch('server.api.activities.db.admin.Activity.load_json', return_value=fake_activity)

    payload = json.dumps({'activity_id': 'OLD1', 'title': 'Imported'})
    response = authenticated_client.post('/activities/import', json={'payload': payload})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': True,
        'rewards': [],
        'badges': [],
        'activity_id': 'NEW1',
    }
    mock_load_json.assert_called_once_with(payload)
    fake_activity.add_participant.assert_called_once_with(fake_user)
    fake_activity.set_owner_status.assert_called_once_with(fake_user, True)


def test_import_activity_returns_error_for_invalid_json_payload(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')

    mocker.patch('server.api.activities.db.admin.User', return_value=fake_user)
    mocker.patch(
        'server.api.activities.db.admin.Activity.load_json',
        side_effect=json.JSONDecodeError('Expecting value', '}', 0),
    )

    response = authenticated_client.post('/activities/import', json={'payload': '}'})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': False,
        'rewards': [],
        'badges': [],
        'message': 'Failed to import activity. JSON syntax error at line 1, column 1: Expecting value.',
    }


def test_import_activity_returns_error_for_missing_field(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')

    mocker.patch('server.api.activities.db.admin.User', return_value=fake_user)
    mocker.patch(
        'server.api.activities.db.admin.Activity.load_json',
        side_effect=KeyError('title'),
    )

    response = authenticated_client.post('/activities/import', json={'payload': '{}'})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': False,
        'rewards': [],
        'badges': [],
        'message': 'Failed to import activity. Missing required field: title.',
    }


def test_import_activity_returns_error_for_server_failure(authenticated_client, mocker):
    fake_user = SimpleNamespace(username='alice')

    mocker.patch('server.api.activities.db.admin.User', return_value=fake_user)
    mocker.patch(
        'server.api.activities.db.admin.Activity.load_json',
        side_effect=RuntimeError('db failed'),
    )

    response = authenticated_client.post('/activities/import', json={'payload': '{}'})

    assert response.status_code == 200
    assert response.get_json() == {
        'success': False,
        'rewards': [],
        'badges': [],
        'message': 'Failed to import activity because the server encountered an error.',
    }


def test_add_user_to_activity_requires_admin(authenticated_client, mocker):
    '''Test that only admin users can add users to activities.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=False)

    mocker.patch('server.api.activities.db.admin.User', return_value=fake_admin_user)

    response = authenticated_client.post(
        '/activities/add-user',
        json={'activity_id': 'DS1', 'username': 'target_user', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is False
    assert 'permission' in response.get_json()['message'].lower()


def test_add_user_to_activity_by_admin_success_as_participant(authenticated_client, mocker):
    '''Test admin can add a user as a participant to a activity.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='target_user', exists=lambda: True)
    fake_activity = mocker.Mock()
    fake_activity.exists.return_value = True

    mocker.patch('server.api.activities.db.admin.User', side_effect=[fake_admin_user, fake_target_user])
    mocker.patch('server.api.activities.db.admin.Activity', return_value=fake_activity)

    response = authenticated_client.post(
        '/activities/add-user',
        json={'activity_id': 'DS1', 'username': 'target_user', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is True
    fake_activity.add_participant.assert_called_once_with(fake_target_user)
    fake_activity.set_owner_status.assert_called_once_with(fake_target_user, False)


def test_add_user_to_activity_by_admin_success_as_owner(authenticated_client, mocker):
    '''Test admin can add a user as an owner to a activity.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='target_user', exists=lambda: True)
    fake_activity = mocker.Mock()
    fake_activity.exists.return_value = True

    mocker.patch('server.api.activities.db.admin.User', side_effect=[fake_admin_user, fake_target_user])
    mocker.patch('server.api.activities.db.admin.Activity', return_value=fake_activity)

    response = authenticated_client.post(
        '/activities/add-user',
        json={'activity_id': 'DS1', 'username': 'target_user', 'is_owner': True},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is True
    fake_activity.add_participant.assert_called_once_with(fake_target_user)
    fake_activity.set_owner_status.assert_called_once_with(fake_target_user, True)


def test_add_user_to_activity_activity_not_found(authenticated_client, mocker):
    '''Test adding a user to a non-existent activity fails.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='target_user')
    fake_activity = mocker.Mock()
    fake_activity.exists.return_value = False

    mocker.patch('server.api.activities.db.admin.User', side_effect=[fake_admin_user, fake_target_user])
    mocker.patch('server.api.activities.db.admin.Activity', return_value=fake_activity)

    response = authenticated_client.post(
        '/activities/add-user',
        json={'activity_id': 'NONEXISTENT', 'username': 'target_user', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is False
    assert 'does not exist' in response.get_json()['message'].lower()


def test_add_user_to_activity_user_not_found(authenticated_client, mocker):
    '''Test adding a non-existent user to a activity fails.'''
    fake_admin_user = SimpleNamespace(username='admin_user', is_admin=True)
    fake_target_user = SimpleNamespace(username='nonexistent', exists=lambda: False)
    fake_activity = mocker.Mock()
    fake_activity.exists.return_value = True

    # Create a Mock object that tracks calls and returns appropriate values
    user_mock = mocker.Mock(side_effect=[fake_admin_user, fake_target_user])

    mocker.patch('server.api.activities.db.admin.User', user_mock)
    mocker.patch('server.api.activities.db.admin.Activity', return_value=fake_activity)

    response = authenticated_client.post(
        '/activities/add-user',
        json={'activity_id': 'DS1', 'username': 'nonexistent', 'is_owner': False},
    )

    assert response.status_code == 200
    assert response.get_json()['success'] is False
    assert 'user does not exist' in response.get_json()['message'].lower()
