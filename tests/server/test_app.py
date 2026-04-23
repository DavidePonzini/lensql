from server import create_app


def test_create_app_registers_expected_blueprints():
    app = create_app()

    assert 'auth' in app.blueprints
    assert 'datasets' in app.blueprints
    assert 'exercise' in app.blueprints
    assert 'message' in app.blueprints
    assert 'query' in app.blueprints
    assert 'user' in app.blueprints
    assert 'navigation' in app.blueprints


def test_create_app_sets_expected_core_config():
    app = create_app()

    assert app.config['JWT_TOKEN_LOCATION'] == ['cookies']
    assert app.config['JWT_ACCESS_COOKIE_PATH'] == '/api'
    assert app.config['JWT_REFRESH_COOKIE_PATH'] == '/api/auth/refresh'
    assert app.config['JWT_COOKIE_CSRF_PROTECT'] is False
