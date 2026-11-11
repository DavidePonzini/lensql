import json
from datetime import datetime

from server.db.admin.activities import Activity
from sqlscope import Dialect


def test_rename_id_updates_instance_after_persistence(mocker):
    fetch = mocker.patch('server.db.admin.activities.db.execute_and_fetch', return_value=[('NEW-ID',)])
    activity = Activity('OLD')
    assert activity.rename_id('NEW-ID') is True
    assert activity.activity_id == 'NEW-ID'
    assert fetch.call_args.args[1] == {'activity_id': 'OLD', 'new_id': 'NEW-ID'}


def test_rename_missing_activity_leaves_instance_unchanged(mocker):
    mocker.patch('server.db.admin.activities.db.execute_and_fetch', return_value=[])
    activity = Activity('OLD')
    assert activity.rename_id('NEW') is False
    assert activity.activity_id == 'OLD'


def test_dump_json_serializes_activity_and_exercises(mocker):
    fetch = mocker.patch(
        'server.db.admin.activities.db.execute_and_fetch',
        side_effect=[
            [[
                'Activity title',
                'Activity description',
                'SELECT 1;',
                'public',
                Dialect.POSTGRES.value,
                'analytics',
            ]],
            [[
                'Exercise title',
                'Solve this',
                json.dumps(['SELECT 1']),
                True,
                3,
                7,
                ['LO1', 'LO2'],
            ]],
        ],
    )

    dumped = json.loads(Activity('ds1').dump_json())

    assert fetch.call_count == 2
    assert dumped == {
        'title': 'Activity title',
        'description': 'Activity description',
        'activity_str': 'SELECT 1;',
        'search_path': 'public',
        'dbms': Dialect.POSTGRES.value,
        'domain': 'analytics',
        'exercises': [{
            'title': 'Exercise title',
            'request': 'Solve this',
            'solutions': ['SELECT 1'],
            'is_hidden': True,
            'difficulty': 3,
            'error': 7,
            'learning_objectives': ['LO1', 'LO2'],
        }],
    }


def test_load_json_creates_activity_and_exercises(mocker):
    created_activity = mocker.Mock()
    created_activity.activity_id = 'new-ds'

    create_activity = mocker.patch(
        'server.db.admin.activities.Activity.create',
        return_value=created_activity,
    )
    create_exercise = mocker.patch('server.db.admin.activities.Exercise.create')
    created_exercise = mocker.Mock()
    create_exercise.return_value = created_exercise

    activity = Activity.load_json(json.dumps({
        'title': 'Imported activity',
        'description': 'Imported description',
        'activity_str': 'SELECT 1;',
        'search_path': 'public',
        'dbms': Dialect.POSTGRES.value,
        'domain': 'analytics',
        'exercises': [{
            'title': 'Imported exercise',
            'request': 'Solve this',
            'solutions': ['SELECT 1'],
            'is_hidden': True,
            'difficulty': 5,
            'error': 9,
            'learning_objectives': ['LO1', 'LO2'],
        }],
    }))

    assert activity is created_activity
    create_activity.assert_called_once_with(
        title='Imported activity',
        description='Imported description',
        activity_str='SELECT 1;',
        domain='analytics',
        search_path='public',
        dbms=Dialect.POSTGRES.value,
    )
    created_activity.add_participant.assert_called_once()
    assert created_activity.add_participant.call_args.args[0].username == 'lens'
    created_activity.set_owner_status.assert_called_once()
    owner_args = created_activity.set_owner_status.call_args.args
    assert owner_args[0].username == 'lens'
    assert owner_args[1] is True

    create_exercise.assert_called_once()
    exercise_kwargs = create_exercise.call_args.kwargs
    assert exercise_kwargs == {
        'title': 'Imported exercise',
        'user': exercise_kwargs['user'],
        'activity_id': 'new-ds',
        'request': 'Solve this',
        'solutions': ['SELECT 1'],
        'difficulty': 5,
        'error': 9,
    }
    assert exercise_kwargs['user'].username == 'lens'
    created_exercise.set_hidden.assert_called_once_with(True)
    created_exercise.set_learning_objective.assert_any_call('LO1')
    created_exercise.set_learning_objective.assert_any_call('LO2')


def test_shuffle_renames_exercises_in_randomized_order(mocker):
    mocker.patch(
        'server.db.admin.activities.db.execute_and_fetch',
        return_value=[
            [11, 'Request 1', json.dumps(['SELECT 1'])],
            [22, 'Request 2', json.dumps(['SELECT 2'])],
            [33, 'Request 3', json.dumps(['SELECT 3'])],
        ],
    )

    def reverse_order(exercises):
        exercises.reverse()

    shuffle = mocker.patch(
        'server.db.admin.activities.random.shuffle',
        side_effect=reverse_order,
    )
    update = mocker.patch('server.db.admin.activities.Exercise.update')

    Activity('ds1').shuffle(prefix='Task ')

    shuffle.assert_called_once()
    assert update.call_count == 3
    assert [call.kwargs for call in update.call_args_list] == [
        {'title': 'Task 1', 'request': 'Request 3', 'solutions': ['SELECT 3']},
        {'title': 'Task 2', 'request': 'Request 2', 'solutions': ['SELECT 2']},
        {'title': 'Task 3', 'request': 'Request 1', 'solutions': ['SELECT 1']},
    ]


def test_update_persists_optional_activity_window(mocker):
    execute = mocker.patch('server.db.admin.activities.db.execute')
    start = datetime(2026, 10, 1, 9)
    end = datetime(2026, 10, 1, 11)

    Activity('ds1').update(
        title='Activity',
        description='',
        activity_str='',
        search_path='public',
        dbms=Dialect.POSTGRES,
        activity_start_ts=start,
        activity_end_ts=end,
    )

    assert execute.call_args.args[1] == {
        'title': 'Activity',
        'description': '',
        'activity_id': 'ds1',
        'activity': None,
        'search_path': 'public',
        'dbms': Dialect.POSTGRES.value,
        'activity_start_ts': start,
        'activity_end_ts': end,
    }
