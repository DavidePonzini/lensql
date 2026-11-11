from types import SimpleNamespace

import pytest


def generated_exercise():
    return SimpleNamespace(request='List rows', solutions=[SimpleNamespace(sql='SELECT * FROM item')],
                           difficulty=SimpleNamespace(value=1), error=SimpleNamespace(value=2))


def test_generated_activity_saves_all_exercises_and_teacher_atomically(mocker):
    from server.generation import generate_activity
    sandbox = mocker.Mock(hostname='test', port=5432, admin_username='postgres')
    mocker.patch('server.generation.get_database', return_value=sandbox)
    assignment = SimpleNamespace(dataset=mocker.Mock(), exercises=[generated_exercise(), generated_exercise()])
    assignment.dataset.to_sql.return_value = 'CREATE TABLE item (id int);'
    mocker.patch('server.generation.sqlexercise.generate_assignment', return_value=assignment)
    connection = mocker.MagicMock()
    connection.__enter__.return_value = connection
    connection.fetch_one.return_value = ('NEW',)
    mocker.patch('server.generation.db.connect', return_value=connection)
    assert generate_activity(SimpleNamespace(username='alice'), [(1, 1), (1, 1)], title='Practice', prefix='Task ') == 'NEW'
    calls = connection.execute.call_args_list
    assert len(calls) == 4
    assert all(call.kwargs['commit'] is False for call in calls)
    assert 'activity_members' in str(calls[1].args[0]) and 'TRUE' in str(calls[1].args[0])
    assert calls[1].args[1]['username'] == 'alice'
    assert [call.args[1]['title'] for call in calls[2:]] == ['Task 1', 'Task 2']
    connection.commit.assert_called_once()


def test_empty_generation_does_not_save_activity(mocker):
    from server.generation import generate_activity
    mocker.patch('server.generation.get_database')
    mocker.patch('server.generation.sqlexercise.generate_assignment',
                 return_value=SimpleNamespace(exercises=[]))
    connect = mocker.patch('server.generation.db.connect')
    with pytest.raises(ValueError, match='any exercises'):
        generate_activity(SimpleNamespace(username='alice'), [(1, 1), (1, 1)], title='Practice', prefix='Task ')
    connect.assert_not_called()


def test_save_failure_does_not_commit_partial_activity(mocker):
    from server.generation import generate_activity
    mocker.patch('server.generation.get_database')
    assignment = SimpleNamespace(dataset=mocker.Mock(), exercises=[generated_exercise()])
    assignment.dataset.to_sql.return_value = 'CREATE TABLE item (id int);'
    mocker.patch('server.generation.sqlexercise.generate_assignment', return_value=assignment)
    connection = mocker.MagicMock()
    connection.__enter__.return_value = connection
    connection.fetch_one.return_value = ('NEW',)
    connection.execute.side_effect = [None, None, RuntimeError('Insert failed')]
    mocker.patch('server.generation.db.connect', return_value=connection)
    with pytest.raises(RuntimeError):
        generate_activity(SimpleNamespace(username='alice'), [(1, 1)], title='Practice', prefix='Task ')
    connection.commit.assert_not_called()
    assert connection.__exit__.call_args.args[0] is RuntimeError


def test_custom_dataset_is_used_and_preserved(mocker):
    from server.generation import generate_activity
    mocker.patch('server.generation.get_database')
    assignment = SimpleNamespace(dataset=mocker.Mock(), exercises=[generated_exercise()])
    generator = mocker.patch('server.generation.sqlexercise.generate_assignment', return_value=assignment)
    connection = mocker.MagicMock()
    connection.__enter__.return_value = connection
    connection.fetch_one.return_value = ('CUSTOM',)
    mocker.patch('server.generation.db.connect', return_value=connection)
    sql = 'CREATE SCHEMA school; CREATE TABLE school.item (id int); INSERT INTO school.item VALUES (1);'
    generate_activity(SimpleNamespace(username='alice'), [(1, 1)], title='Practice', prefix='Task ',
                      dataset_str=sql, search_path='school')
    assert 'CREATE TABLE item' in generator.call_args.kwargs['dataset_str']
    assert 'school.item' not in generator.call_args.kwargs['dataset_str']
    saved = connection.execute.call_args_list[0].args[1]
    assert sql in saved['activity']
    assert saved['activity'].endswith("SELECT set_config('search_path', 'school', false);")
    assert saved['search_path'] == 'school'
    assignment.dataset.to_sql.assert_not_called()


def test_partial_generation_saves_successful_exercises(mocker):
    from server.generation import generate_activity
    mocker.patch('server.generation.get_database')
    assignment = SimpleNamespace(dataset=mocker.Mock(), exercises=[generated_exercise()])
    assignment.dataset.to_sql.return_value = 'CREATE TABLE item (id int);'
    mocker.patch('server.generation.sqlexercise.generate_assignment', return_value=assignment)
    connection = mocker.MagicMock()
    connection.__enter__.return_value = connection
    connection.fetch_one.return_value = ('PARTIAL',)
    mocker.patch('server.generation.db.connect', return_value=connection)
    progress = mocker.Mock()
    assert generate_activity(SimpleNamespace(username='alice'), [(1, 1), (1, 1)],
                             title='Practice', prefix='Task ', on_progress=progress) == 'PARTIAL'
    assert len(connection.execute.call_args_list) == 3
    connection.commit.assert_called_once()
    assert progress.call_args.args[0]['completed'] == 1
