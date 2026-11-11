from types import SimpleNamespace

import pytest


def valid_request():
    from sqlexercise.error_requirements import ERROR_REQUIREMENTS_MAP
    error = next(e for e in ERROR_REQUIREMENTS_MAP if not e.definition.is_deprecated)
    return {'title': 'Practice', 'prefix': 'Task ', 'errors': [{'error_id': error.value, 'count': 2}]}


@pytest.fixture
def user(mocker):
    user = mocker.Mock(username='alice', ai_generation_credits=7)
    mocker.patch('server.api.activities.db.admin.User', return_value=user)
    return user


def test_insufficient_credits_does_not_generate(authenticated_client, mocker, user):
    user.reserve_generation_credits.return_value = False
    generate = mocker.patch('server.generation.generate_activity')
    response = authenticated_client.post('/activities/generate', json=valid_request()).get_json()
    assert response['success'] is False
    user.reserve_generation_credits.assert_called_once_with(2)
    generate.assert_not_called()


def test_generation_creates_activity_for_requesting_user(authenticated_client, mocker, user):
    generate = mocker.patch('server.generation.generate_activity', return_value='NEW123')
    response = authenticated_client.post('/activities/generate', json=valid_request()).get_json()
    assert response['success'] is True
    assert response['activity_id'] == 'NEW123'
    assert len(generate.call_args.args[1]) == 2
    assert generate.call_args.args[0] is user
    assert generate.call_args.kwargs['prefix'] == 'Task '
    user.refund_generation_credits.assert_not_called()


def test_generation_failure_refunds_credits(authenticated_client, mocker, user):
    mocker.patch('server.generation.generate_activity', side_effect=RuntimeError('Generation failed'))
    response = authenticated_client.post('/activities/generate', json=valid_request()).get_json()
    assert response['success'] is False
    user.refund_generation_credits.assert_called_once_with(2)


@pytest.mark.parametrize('count', [0, -1, 101, 1.5, True, '2', None])
def test_invalid_counts_do_not_spend_credits(authenticated_client, user, count):
    data = valid_request()
    data['errors'][0]['count'] = count
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is False
    user.reserve_generation_credits.assert_not_called()


@pytest.mark.parametrize('payload', [None, [], {}, {'title': 5}, {'title': 'x', 'errors': [None]}])
def test_invalid_generation_payload(authenticated_client, user, payload):
    assert authenticated_client.post('/activities/generate', json=payload).get_json()['success'] is False
    user.reserve_generation_credits.assert_not_called()


def test_student_list_requires_ownership_of_every_activity(authenticated_client, mocker, user):
    activity = mocker.Mock()
    activity.has_owner.side_effect = [True, False]
    mocker.patch('server.api.activities.db.admin.Activity', return_value=activity)
    query = mocker.patch('server.db.admin.connection.db.execute_and_fetch')
    response = authenticated_client.post('/activities/generation-students', json={'activity_ids': ['A', 'B']}).get_json()
    assert response['success'] is False
    query.assert_not_called()
    user.reserve_generation_credits.assert_not_called()


def test_student_list_filters_active_students(authenticated_client, mocker, user):
    activity = mocker.Mock()
    activity.has_owner.return_value = True
    mocker.patch('server.api.activities.db.admin.Activity', return_value=activity)
    query = mocker.patch('server.db.admin.connection.db.execute_and_fetch', return_value=[('bob',), ('carol',)])
    response = authenticated_client.post('/activities/generation-students', json={'activity_ids': ['A', 'B']}).get_json()
    assert response['students'] == ['bob', 'carol']
    sql = str(query.call_args.args[0])
    assert 'DISTINCT username' in sql
    assert 'is_active = TRUE AND is_owner = FALSE' in sql
    user.reserve_generation_credits.assert_not_called()


def test_admin_credits_requires_admin(authenticated_client, mocker):
    user = mocker.Mock(is_admin=False)
    mocker.patch('server.api.users.db.admin.User', return_value=user)
    assert authenticated_client.post('/users/admin/generation-credits', json={}).get_json()['success'] is False
    user.set_ai_generation_credits.assert_not_called()


@pytest.mark.parametrize('credits', [-1, None, 1.2, True, '2', 2147483648])
def test_admin_credits_validates_integer(authenticated_client, mocker, credits):
    user = mocker.Mock(is_admin=True)
    mocker.patch('server.api.users.db.admin.User', return_value=user)
    response = authenticated_client.post('/users/admin/generation-credits', json={'username': 'bob', 'ai_generation_credits': credits})
    assert response.get_json()['success'] is False
    user.set_ai_generation_credits.assert_not_called()


def test_admin_sets_generation_credits(authenticated_client, mocker):
    admin, target = mocker.Mock(is_admin=True), mocker.Mock()
    mocker.patch('server.api.users.db.admin.User', side_effect=[admin, target])
    response = authenticated_client.post('/users/admin/generation-credits', json={'username': 'bob', 'ai_generation_credits': 0})
    assert response.get_json()['success'] is True
    target.set_ai_generation_credits.assert_called_once_with(0)


def test_same_error_can_have_multiple_difficulties(authenticated_client, mocker, user):
    from sqlexercise import DifficultyLevel
    generate = mocker.patch('server.generation.generate_activity', return_value='MIXED')
    data = valid_request()
    error_id = data['errors'][0]['error_id']
    data['errors'] = [{'error_id': error_id, 'difficulty': 1, 'count': 1},
                      {'error_id': error_id, 'difficulty': 3, 'count': 3}]
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is True
    errors = generate.call_args.args[1]
    assert [difficulty for _, difficulty in errors] == [DifficultyLevel.EASY] + [DifficultyLevel.HARD] * 3
    assert all(error.value == error_id for error, _ in errors)
    user.reserve_generation_credits.assert_called_once_with(4)


@pytest.mark.parametrize('difficulty', [0, 4, -1, 'EASY', True, None, 1.5])
def test_invalid_difficulty_does_not_spend_credits(authenticated_client, user, difficulty):
    data = valid_request()
    data['errors'][0]['difficulty'] = difficulty
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is False
    user.reserve_generation_credits.assert_not_called()


def test_custom_dataset_is_forwarded(authenticated_client, mocker, user):
    generate = mocker.patch('server.generation.generate_activity', return_value='CUSTOM')
    data = {**valid_request(), 'dataset_str': 'CREATE TABLE item (id integer); INSERT INTO item VALUES (1);',
            'search_path': 'public'}
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is True
    assert generate.call_args.kwargs['dataset_str'] == data['dataset_str']
    assert generate.call_args.kwargs['search_path'] == 'public'


@pytest.mark.parametrize('dataset', ['SELECT 1;', 'not valid SQL !', 123, 'x' * 2_000_001])
def test_invalid_dataset_does_not_spend_credits(authenticated_client, user, dataset):
    data = {**valid_request(), 'dataset_str': dataset}
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is False
    user.reserve_generation_credits.assert_not_called()


def test_generation_options_identify_errors_for_shared_profile_translations(authenticated_client, user):
    user.list_activities.return_value = []
    response = authenticated_client.get('/activities/generation-options').get_json()
    assert response['success'] is True
    categories = {category['id'] for category in response['categories']}
    assert categories == {'SYN', 'SEM', 'LOG', 'COM'}
    assert all(set(category) == {'id'} for category in response['categories'])
    assert response['errors']
    assert all(error['category'] in categories and 'description' not in error for error in response['errors'])


def test_qualified_dataset_is_accepted(authenticated_client, mocker, user):
    generate = mocker.patch('server.generation.generate_activity', return_value='QUALIFIED')
    sql = 'CREATE SCHEMA school; CREATE TABLE school.item (id int); INSERT INTO school.item VALUES (1);'
    data = {**valid_request(), 'dataset_str': sql, 'search_path': 'school'}
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is True
    assert generate.call_args.kwargs['dataset_str'] == sql


def test_multiple_dataset_schemas_do_not_spend_credits(authenticated_client, user):
    data = {**valid_request(), 'dataset_str': 'CREATE TABLE a.item (id int); CREATE TABLE b.item (id int);'}
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is False
    user.reserve_generation_credits.assert_not_called()


@pytest.mark.parametrize('search_path', [None, '', 123])
def test_automatic_dataset_does_not_require_schema(authenticated_client, mocker, user, search_path):
    generate = mocker.patch('server.generation.generate_activity', return_value='AUTO')
    data = {**valid_request(), 'search_path': search_path}
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is True
    assert generate.call_args.kwargs['search_path'] == 'public'


@pytest.mark.parametrize('search_path', [None, '', '  ', 123])
def test_provided_dataset_requires_schema(authenticated_client, user, search_path):
    data = {**valid_request(), 'dataset_str': 'CREATE TABLE item (id int);', 'search_path': search_path}
    assert authenticated_client.post('/activities/generate', json=data).get_json()['success'] is False
    user.reserve_generation_credits.assert_not_called()
