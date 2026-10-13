from types import SimpleNamespace
import pytest


def test_admin_password_change_requires_admin(authenticated_client, mocker):
    factory = mocker.patch('server.api.auth.db.admin.User', return_value=SimpleNamespace(is_admin=False))
    response = authenticated_client.post('/auth/admin/change-password', json={'username': 'bob', 'new_password': 'Strong123!'})
    assert response.get_json()['success'] is False
    factory.assert_called_once()


@pytest.mark.parametrize('password', ['x', 'weak', '123', ' Strong123! ', 'A1!' + 'é' * 36])
def test_admin_changes_named_user_password(authenticated_client, mocker, password):
    target = mocker.Mock()
    target.exists.return_value = True
    target.change_password.return_value = True
    factory = mocker.patch('server.api.auth.db.admin.User', side_effect=[SimpleNamespace(is_admin=True), target])
    response = authenticated_client.post('/auth/admin/change-password', json={'username': ' bob ', 'new_password': password})
    assert response.get_json()['success'] is True
    assert factory.call_args.args == ('bob',)
    target.change_password.assert_called_once_with(password)
    target.can_login.assert_not_called()
    assert 'new_password' not in response.get_json()


@pytest.mark.parametrize('payload', [None, [], {}, {'username': '', 'new_password': 'Strong123!'},
    {'username': 123, 'new_password': 'Strong123!'}, {'username': 'bob', 'new_password': None},
    {'username': 'bob', 'new_password': ''}])
def test_admin_password_change_rejects_invalid_input(authenticated_client, mocker, payload):
    factory = mocker.patch('server.api.auth.db.admin.User', return_value=SimpleNamespace(is_admin=True))
    response = authenticated_client.post('/auth/admin/change-password', json=payload)
    assert response.get_json()['success'] is False
    factory.assert_called_once()


@pytest.mark.parametrize('exists, changed', [(False, False), (True, False)])
def test_admin_password_change_reports_failure(authenticated_client, mocker, exists, changed):
    target = mocker.Mock()
    target.exists.return_value = exists
    target.change_password.return_value = changed
    mocker.patch('server.api.auth.db.admin.User', side_effect=[SimpleNamespace(is_admin=True), target])
    response = authenticated_client.post('/auth/admin/change-password', json={'username': 'bob', 'new_password': 'Strong123!'})
    assert response.get_json()['success'] is False
    if not exists:
        target.change_password.assert_not_called()


def test_login_returns_error_for_invalid_credentials(client, mocker):
    fake_user = SimpleNamespace(can_login=lambda password: False)

    mocker.patch('server.api.auth.db.admin.User', return_value=fake_user)

    response = client.post('/auth/login', json={
        'username': 'alice',
        'password': 'wrong-password',
    })

    assert response.status_code == 200
    assert response.get_json()['success'] is False


def test_login_sets_auth_cookies_for_valid_credentials(client, mocker):
    fake_user = SimpleNamespace(can_login=lambda password: True)

    mocker.patch('server.api.auth.db.admin.User', return_value=fake_user)

    response = client.post('/auth/login', json={
        'username': 'alice',
        'password': 'correct-password',
    })

    assert response.status_code == 200
    assert response.get_json()['success'] is True

    cookies = response.headers.getlist('Set-Cookie')
    assert any('access_token_cookie=' in cookie for cookie in cookies)
    assert any('refresh_token_cookie=' in cookie for cookie in cookies)


def test_register_returns_error_when_user_exists(client, mocker):
    fake_user = SimpleNamespace(exists=lambda: True)

    mocker.patch('server.api.auth.db.admin.User', return_value=fake_user)

    response = client.post('/auth/register', json={
        'username': 'alice',
        'password': 'password123',
        'school': 'LensQL High',
        'is_teacher': False,
    })

    assert response.status_code == 200
    assert response.get_json()['success'] is False


def test_register_uses_default_datasets_and_registers_user(client, mocker):
    fake_user = SimpleNamespace(exists=lambda: False)
    created_dataset_ids = []
    register_calls = []

    def dataset_factory(dataset_id):
        created_dataset_ids.append(dataset_id)
        return SimpleNamespace(dataset_id=dataset_id)

    def register_user(user, password, **kwargs):
        register_calls.append((user, password, kwargs))
        return True

    mocker.patch('server.api.auth.db.admin.User', return_value=fake_user)
    mocker.patch('server.api.auth.db.admin.Dataset', side_effect=dataset_factory)
    mocker.patch('server.api.auth.db.register_user', side_effect=register_user)

    response = client.post('/auth/register', json={
        'username': 'alice',
        'password': 'password123',
        'school': 'LensQL High',
        'is_teacher': True,
    })

    assert response.status_code == 200
    assert response.get_json()['success'] is True
    assert created_dataset_ids == ['_EXPLORE', '_WELCOME_MIEDEMA']
    assert len(register_calls) == 1
    _, password, kwargs = register_calls[0]
    assert password == 'password123'
    assert kwargs['school'] == 'LensQL High'
    assert kwargs['is_teacher'] is True
    assert [dataset.dataset_id for dataset in kwargs['datasets']] == ['_EXPLORE', '_WELCOME_MIEDEMA']
