import json

from server.db.admin.datasets import Dataset


def test_dump_json_serializes_dataset_and_exercises(mocker):
    fetch = mocker.patch(
        'server.db.admin.datasets.db.execute_and_fetch',
        side_effect=[
            [[
                'Dataset title',
                'Dataset description',
                'SELECT 1;',
                'public',
                'postgresql',
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

    dumped = json.loads(Dataset('ds1').dump_json())

    assert fetch.call_count == 2
    assert dumped == {
        'title': 'Dataset title',
        'description': 'Dataset description',
        'dataset_str': 'SELECT 1;',
        'search_path': 'public',
        'dbms': 'postgresql',
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


def test_load_json_creates_dataset_and_exercises(mocker):
    created_dataset = mocker.Mock()
    created_dataset.dataset_id = 'new-ds'

    create_dataset = mocker.patch(
        'server.db.admin.datasets.Dataset.create',
        return_value=created_dataset,
    )
    create_exercise = mocker.patch('server.db.admin.datasets.Exercise.create')
    created_exercise = mocker.Mock()
    create_exercise.return_value = created_exercise

    dataset = Dataset.load_json(json.dumps({
        'title': 'Imported dataset',
        'description': 'Imported description',
        'dataset_str': 'SELECT 1;',
        'search_path': 'public',
        'dbms': 'postgresql',
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

    assert dataset is created_dataset
    create_dataset.assert_called_once_with(
        title='Imported dataset',
        description='Imported description',
        dataset_str='SELECT 1;',
        domain='analytics',
        search_path='public',
        dbms='postgresql',
    )
    created_dataset.add_participant.assert_called_once()
    assert created_dataset.add_participant.call_args.args[0].username == 'lens'
    created_dataset.set_owner_status.assert_called_once()
    owner_args = created_dataset.set_owner_status.call_args.args
    assert owner_args[0].username == 'lens'
    assert owner_args[1] is True

    create_exercise.assert_called_once()
    exercise_kwargs = create_exercise.call_args.kwargs
    assert exercise_kwargs == {
        'title': 'Imported exercise',
        'user': exercise_kwargs['user'],
        'dataset_id': 'new-ds',
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
        'server.db.admin.datasets.db.execute_and_fetch',
        return_value=[
            [11, 'Request 1', json.dumps(['SELECT 1'])],
            [22, 'Request 2', json.dumps(['SELECT 2'])],
            [33, 'Request 3', json.dumps(['SELECT 3'])],
        ],
    )

    def reverse_order(exercises):
        exercises.reverse()

    shuffle = mocker.patch(
        'server.db.admin.datasets.random.shuffle',
        side_effect=reverse_order,
    )
    update = mocker.patch('server.db.admin.datasets.Exercise.update')

    Dataset('ds1').shuffle(prefix='Task ')

    shuffle.assert_called_once()
    assert update.call_count == 3
    assert [call.kwargs for call in update.call_args_list] == [
        {'title': 'Task 1', 'request': 'Request 3', 'solutions': ['SELECT 3']},
        {'title': 'Task 2', 'request': 'Request 2', 'solutions': ['SELECT 2']},
        {'title': 'Task 3', 'request': 'Request 1', 'solutions': ['SELECT 1']},
    ]
