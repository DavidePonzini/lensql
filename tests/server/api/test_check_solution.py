from types import SimpleNamespace

from server.gamification.reward import Reward
from server.sql.code import SQLCode
from server.sql.result import QueryResultMessage


def test_check_solution_returns_not_enough_coins_message(authenticated_client, mocker):
    fake_user = SimpleNamespace(
        username='alice',
        get_coins=lambda: 0,
    )
    fake_exercise = SimpleNamespace(
        dataset_id='dataset-1',
        count_attempts=lambda user: 3,
    )
    fake_dataset = SimpleNamespace(
        dbms='postgresql',
        search_path='public',
    )

    mocker.patch('server.api.queries.db.admin.User', return_value=fake_user)
    mocker.patch('server.api.queries.db.admin.Exercise', return_value=fake_exercise)
    mocker.patch('server.api.queries.db.admin.Dataset', return_value=fake_dataset)
    mocker.patch(
        'server.api.queries.gamification.rewards.Actions.Exercise.check_solution_cost',
        return_value=Reward('Checked solution', coins=-5),
    )
    get_database = mocker.patch('server.api.queries.db.users.get_database')

    response = authenticated_client.post('/queries/check-solution', json={
        'query': 'SELECT 1',
        'exercise_id': 7,
    })

    assert response.status_code == 200
    assert response.get_json() == [{
        'success': True,
        'builtin': True,
        'query': 'CHECK_SOLUTION',
        'type': 'message',
        'data': "You don't have enough coins to use this feature. Check the Profile page to learn how to earn more.",
        'id': None,
        'rewards': [],
        'badges': [],
        'attempts': 3,
    }]
    get_database.assert_not_called()


def test_check_solution_returns_rewards_and_logs_context(authenticated_client, mocker):
    fake_user = SimpleNamespace(
        username='alice',
        get_coins=lambda: 10,
        count_exercises_solved=lambda: 1,
        has_badge=lambda reason: False,
        add_rewards=mocker.stub(name='add_rewards'),
    )
    fake_exercise = SimpleNamespace(
        dataset_id='dataset-1',
        count_attempts=lambda user: 0,
        solutions=['SELECT 1'],
        has_been_solved_by_user=lambda user: False,
    )
    fake_dataset = SimpleNamespace(
        dbms='postgresql',
        search_path='public',
    )
    fake_result = QueryResultMessage('Correct', query=SQLCode('CHECK_SOLUTION', builtin=True))
    fake_check = SimpleNamespace(
        correct=True,
        execution_success=True,
        result=fake_result,
    )
    fake_database = SimpleNamespace(
        get_search_path=lambda: 'public',
        check_query_solution=lambda **kwargs: fake_check,
        get_columns=lambda: ['columns'],
        get_unique_columns=lambda: ['unique_columns'],
    )
    fake_batch = SimpleNamespace()
    fake_query = SimpleNamespace(
        query_id=321,
        log_context=mocker.stub(name='log_context'),
        log_errors=mocker.stub(name='log_errors'),
        log_solution_attempt=mocker.stub(name='log_solution_attempt'),
    )

    mocker.patch('server.api.queries.db.admin.User', return_value=fake_user)
    mocker.patch('server.api.queries.db.admin.Exercise', return_value=fake_exercise)
    mocker.patch('server.api.queries.db.admin.Dataset', return_value=fake_dataset)
    mocker.patch('server.api.queries.db.users.get_database', return_value=fake_database)
    mocker.patch('server.api.queries.db.admin.QueryBatch.log', return_value=fake_batch)
    mocker.patch('server.api.queries.db.admin.Query.log', return_value=fake_query)
    mocker.patch('server.api.queries.build_catalog', return_value='catalog')
    mocker.patch('server.api.queries.get_errors', return_value=['error'])

    response = authenticated_client.post('/queries/check-solution', json={
        'query': 'SELECT 1',
        'exercise_id': 7,
    })

    payload = response.get_json()

    assert response.status_code == 200
    assert payload[0]['success'] is True
    assert payload[0]['builtin'] is True
    assert payload[0]['query'] == 'CHECK_SOLUTION'
    assert payload[0]['id'] is None
    assert payload[0]['attempts'] == 1
    assert payload[0]['rewards'] == [
        {'reason': 'Checked solution', 'experience': 0, 'coins': 0},
        {'reason': 'Exercise solved for the first time', 'experience': 1000, 'coins': 100},
    ]
    assert payload[0]['badges'] == [
        {'reason': 'exercise_solutions.1', 'experience': 0, 'coins': 10},
    ]

    fake_query.log_context.assert_called_once_with(
        columns=['columns'],
        unique_columns=['unique_columns'],
    )
    fake_query.log_solution_attempt.assert_called_once_with(True)
    fake_user.add_rewards.assert_called_once()
