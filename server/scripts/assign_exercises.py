import sys

from server.db.admin import Dataset, Exercise, User
from sql_error_taxonomy import SqlErrors
from sql_assignment_generator import DifficultyLevel
import random

import dav_tools

def find_exercise_for_error(exercises: list[Exercise], error: SqlErrors, difficulty: DifficultyLevel) -> Exercise | None:
    '''Find an exercise in the list that matches the given SQL error pattern.'''
    for exercise in exercises:

        if not exercise.error or not exercise.difficulty:
            continue

        if exercise.error == error and DifficultyLevel(exercise.difficulty) == difficulty:
            return exercise
    return None


ADMIN_USER = User('lens')

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('username', help='Username of the user to assign exercises to')
    dav_tools.argument_parser.add_argument('dataset', help='ID of the dataset containing exercises to assign')
    dav_tools.argument_parser.add_argument('-d', '--dataset-name', help='Name of the new dataset')
    dav_tools.argument_parser.add_argument('-p', '--exercise-prefix', help='Prefix for the shuffled exercise titles', default='Exercise ')
    dav_tools.argument_parser.add_argument('--allowed-datasets', nargs='*', help='Only consider queries from these datasets for error extraction')
    dav_tools.argument_parser.add_argument('--allowed-goals', nargs='*', choices=['FOCUSED', 'CHECK_SOLUTION'], default=['FOCUSED', 'CHECK_SOLUTION'], help='Only consider queries with these goals for error extraction')
    dav_tools.argument_parser.add_argument('--exercises-amount', type=int, default=12, help='Number of exercises to assign')
    dav_tools.argument_parser.add_argument('--dry-run', action='store_true', help='Perform a dry run without actually assigning exercises')
    dav_tools.argument_parser.parse_args()

    user = User(dav_tools.argument_parser.args.username)
    template_dataset = Dataset(dav_tools.argument_parser.args.dataset)
    template_exercises = template_dataset.list_all_exercises()

    exercises_amount = dav_tools.argument_parser.args.exercises_amount

    if len(template_exercises) == 0:
        dav_tools.messages.critical_error('No exercises found, or the exercises don\'t target a specific error.')

    error_patterns = user.get_error_occurrencies(
        dataset_ids=dav_tools.argument_parser.args.allowed_datasets,
        allowed_query_goals=dav_tools.argument_parser.args.allowed_goals
    )

    # dav_tools.messages.debug(f'Extracted {len(error_patterns)} error patterns for user "{user.username}".')

    # Sort error patterns by frequency in descending order
    error_patterns = sorted(error_patterns, key=lambda x: x[1], reverse=True)

    exercises_found:set[Exercise] = set()
    exercises_not_found: set[tuple[SqlErrors, DifficultyLevel]] = set()

    def find_exercise(error: SqlErrors, difficulty: DifficultyLevel):
        exercise = find_exercise_for_error(template_exercises, error, difficulty)
        if exercise is not None:
            exercises_found.add(exercise)
            # dav_tools.messages.debug(f'Found "{exercise.title}" for error "{error.definition.name}" ({error.value}) at {difficulty.name} difficulty.')
        else:
            exercises_not_found.add((error, difficulty))
            # dav_tools.messages.warning(f'No exercise found for error "{error.definition.name}" ({error.value}) at {difficulty.name} difficulty.')

    for error_pattern, count in error_patterns:
        if len(exercises_found) < exercises_amount // 2:
            find_exercise(error_pattern, DifficultyLevel.EASY)
            find_exercise(error_pattern, DifficultyLevel.MEDIUM)
        elif len(exercises_found) < exercises_amount:
            find_exercise(error_pattern, DifficultyLevel.MEDIUM)
            find_exercise(error_pattern, DifficultyLevel.HARD)
        else:
            break
    
    # add random exercises from the template dataset until we have exercises_amount exercises in total
    remaining_exercises = [exercise for exercise in template_exercises if exercise not in exercises_found]
    random_exercises = random.sample(template_exercises, k=max(0, exercises_amount - len(exercises_found)))

    if len(random_exercises) > 0:
        dav_tools.messages.warning(f'Adding {len(random_exercises)} random exercises for user "{user.username}".')
    for exercise in random_exercises:
        exercises_found.add(exercise)

    if len(exercises_found) == 0:
        dav_tools.messages.critical_error(f'No suitable exercises found for user "{user.username}".')

    # if dry run, print the exercises that would be assigned and exit
    if dav_tools.argument_parser.args.dry_run:
        dav_tools.messages.success(f'Dry run complete. The following exercises would be assigned to user "{user.username}":')
        for exercise in exercises_found:
            print(f'    - {exercise.title} (Error: {exercise.error}, Difficulty: {exercise.difficulty})', file=sys.stderr)
        exit(0)

    # Create a new dataset for the user and assign the found exercises to it
    dataset = Dataset.create(
        title=dav_tools.argument_parser.args.dataset_name or template_dataset.name,
        description=template_dataset.description,
        dataset_str=template_dataset.dataset_str,
        domain=template_dataset.domain,
        search_path=template_dataset.search_path,
        dbms=template_dataset.dbms,
    )
    
    for exercise in exercises_found:
        Exercise.create(
            title=exercise.title,
            user=ADMIN_USER,
            dataset_id=dataset.dataset_id,
            request=exercise.request,
            solutions=exercise.solutions,
            difficulty=exercise.difficulty,
            error=exercise.error
        )

    dataset.add_participant(user)
    dataset.shuffle(dav_tools.argument_parser.args.exercise_prefix)

    dav_tools.messages.success(f'Assigned {len(exercises_found)} exercises to "{user.username}". Dataset ID: {dataset.dataset_id}')