import dav_tools
import sql_assignment_generator
from sql_assignment_generator import SqlErrors, DifficultyLevel
from server.db.admin import Dataset, Exercise, User
import random
from datetime import datetime

TITLE = 'Targeted Practice'
SUBTITLES = [
    'Short practice sets tailored to your learning progress.',
]

admin_user = User('lens')

def generate_assignment(
    user: User,
    errors: list[tuple[SqlErrors, DifficultyLevel]],
    domain: str | None = None,
) -> Dataset:
    '''Generate SQL assignments based on specified SQL errors and difficulty levels.'''

    exercise_counter = 0
    def exercise_naming_func(error: SqlErrors, difficulty: DifficultyLevel) -> str:
        nonlocal exercise_counter
        exercise_counter += 1
        return f'Exercise {exercise_counter}'

    assignment = sql_assignment_generator.generate_assignment(
        errors=errors,
        domain=domain,
        shuffle_exercises=True,
        naming_func=exercise_naming_func,
        max_dataset_attempts=10,
        max_exercise_attempts=10,
        max_unique_attempts=10,
    )

    # format: 'p_250113'
    schema_name = datetime.now().strftime('p_%y%m%d')
    
    # Save dataset to the database
    dataset = Dataset.create(
        title=TITLE,
        description=random.choice(SUBTITLES),
        dataset_str=assignment.dataset.to_sql(schema_name),
        domain=domain
    )

    # Add admin user as participant and set as owner
    dataset.add_participant(admin_user)
    dataset.set_owner_status(admin_user, True)

    # Save each exercise to the database
    for exercise_data in assignment.exercises:
        Exercise.create(
            title=exercise_data.title,
            user=admin_user,
            dataset_id=dataset.dataset_id,
            request=exercise_data.request,
            solutions=[query.sql for query in exercise_data.solutions],
            search_path=schema_name,
            difficulty=exercise_data.difficulty.value,
            error=exercise_data.error.value
        )

    # Add the specified user as participant
    dataset.add_participant(user)

    return dataset


if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('user', help='Username to assign the generated exercises to')
    dav_tools.argument_parser.add_argument('--assign_to', help='Username to assign the generated exercises to (alternative to user)')
    dav_tools.argument_parser.add_argument('--domain', help='Optional domain to filter exercises by')
    dav_tools.argument_parser.add_argument('--dataset', help='Only extract error patterns from this dataset')
    dav_tools.argument_parser.parse_args()

    user = User(dav_tools.argument_parser.args.user)

    if dav_tools.argument_parser.args.dataset:
        error_stats = user.get_error_stats(dataset_id=dav_tools.argument_parser.args.dataset)['errors']
    else:
        error_stats = user.get_error_stats()['errors']

    sorted_error_stats = sorted(error_stats, key=lambda item: item['count'], reverse=True)

    if not sorted_error_stats:
        dav_tools.messages.error(f'No error stats found for user {user.username}. Cannot generate targeted assignment.')
        exit()

    dav_tools.messages.info(f'Extracted error stats for user {user.username}:')
    for i, error in enumerate(sorted_error_stats):
        error_id = error['error_id']
        error_name = SqlErrors(error_id).name if error_id in SqlErrors._value2member_map_ else 'Unknown Error'
        dav_tools.messages.message(f'{i+1}. {error_name}: {error["count"]}')

    top_n = int(dav_tools.messages.ask('Select last error number to target'))

    top_errors = sorted_error_stats[:top_n]

    errors: list[tuple[SqlErrors, DifficultyLevel]] = []

    for error in top_errors:
        errors.append((SqlErrors(error['error_id']), DifficultyLevel.EASY))
        errors.append((SqlErrors(error['error_id']), DifficultyLevel.MEDIUM))
        errors.append((SqlErrors(error['error_id']), DifficultyLevel.HARD))

    assign_to = dav_tools.argument_parser.args.assign_to
    if assign_to:
        assign_to_user = User(assign_to)
    else:
        assign_to_user = user

    dataset = generate_assignment(assign_to_user, errors)

    dav_tools.messages.info(f'Dataset ID: {dataset.dataset_id}')