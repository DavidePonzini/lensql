import pytest
from flask_jwt_extended import create_access_token

from server import create_app


@pytest.fixture(autouse=True)
def _set_test_env(monkeypatch):
    monkeypatch.setenv('JWT_SECRET_KEY', 'x' * 32)
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(client, app):
    with app.app_context():
        token = create_access_token(identity='alice')

    client.set_cookie('access_token_cookie', token)
    return client
