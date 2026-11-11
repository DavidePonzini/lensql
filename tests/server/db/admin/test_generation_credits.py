from server.db.admin import User


def test_reserve_credits_uses_conditional_update(mocker):
    execute = mocker.patch('server.db.admin.users.db.execute_and_fetch', return_value=[(1,)])
    assert User('alice').reserve_generation_credits(2) is True
    query, data = execute.call_args.args
    assert 'ai_generation_credits >= %(count)s' in str(query)
    assert 'ai_generation_credits - %(count)s' in str(query)
    assert data == {'username': 'alice', 'count': 2}


def test_reserve_credits_returns_false_when_balance_is_insufficient(mocker):
    mocker.patch('server.db.admin.users.db.execute_and_fetch', return_value=[])
    assert User('alice').reserve_generation_credits(2) is False
