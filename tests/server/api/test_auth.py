from types import SimpleNamespace


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
