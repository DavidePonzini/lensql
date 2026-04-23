from server.db.admin.users import User, _compare_hashed_password, _hash_password


def test_user_normalizes_username():
    user = User('alice@example.com')

    assert user.username == 'alice_example_com'


def test_hash_password_round_trip():
    password = 'secret-password'
    hashed = _hash_password(password)

    assert hashed != password
    assert _compare_hashed_password(password, hashed) is True
    assert _compare_hashed_password('wrong-password', hashed) is False
