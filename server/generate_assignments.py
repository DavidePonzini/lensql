import dav_tools
import sql_assignment_generator
from sql_assignment_generator import SqlErrors, DifficultyLevel
from server.db.admin import Dataset, Exercise, User
import random
from datetime import datetime

admin_user = User('lens')

def generate_assignment(
    user: User,
    errors: list[tuple[SqlErrors, DifficultyLevel]],
    *,
    title: str | None = None,
    description: str | None = None,
    dataset_id: str | None = None,
    input_dataset_str: str | None = None,
    input_exercise_count: int | None = None,
    domain: str | None = None,
    sql_dialect: str = 'postgres',
    language: str = 'en',
) -> Dataset:
    '''Generate SQL assignments based on specified SQL errors and difficulty levels.'''

    if input_exercise_count is None:
        input_exercise_count = 0
    
    assignment = sql_assignment_generator.generate_assignment(
        errors=errors,
        sql_dialect=sql_dialect,
        language=language,
        dataset_str=input_dataset_str,
        domain=domain,
        shuffle_exercises=True,
        max_dataset_attempts=10,
        max_exercise_attempts=10,
        max_unique_attempts=10,
    )

    if title is None:
        if language == 'it':
            title = 'Pratica personalizzata'
        else:
            title = 'Targeted Practice Set'
    else:
        if language == 'it':
            title = f'Pratica personalizzata: {title}'
        else:
            title = f'Targeted Practice Set: {title}'
    if description is None:
        if language == 'it':
            description = 'Esercizi personalizzati basati sul tuo progresso di apprendimento.'
        else:
            description = 'Practice set tailored to your learning progress.'

    if dataset_id is None:
        # Generate a new dataset

        # format: 'p_250113'
        schema_name = datetime.now().strftime('p_%y%m%d')
        if input_dataset_str is not None:
            dataset_str = input_dataset_str
        else:
            dataset_str = assignment.dataset.to_sql(schema_name)
    
        # Save dataset to the database
        dataset = Dataset.create(
            title=title,
            description=description,
            dataset_str=dataset_str,
            domain=domain,
            search_path=schema_name,
        )
    else:
        # Use existing dataset
        dataset = Dataset(dataset_id)
        

    # Add admin user as participant and set as owner
    dataset.add_participant(admin_user)
    dataset.set_owner_status(admin_user, True)

    exercise_counter = input_exercise_count if input_exercise_count is not None else 0
    def get_exercise_name() -> str:
        nonlocal exercise_counter
        exercise_counter += 1

        if language == 'en':
            return f'Exercise {exercise_counter}'
        if language == 'it':
            return f'Esercizio {exercise_counter}'
        return f'Exercise {exercise_counter}'

    # Save each exercise to the database
    for exercise_data in assignment.exercises:
        Exercise.create(
            title=get_exercise_name(),
            user=admin_user,
            dataset_id=dataset.dataset_id,
            request=exercise_data.request,
            solutions=[query.sql for query in exercise_data.solutions],
            difficulty=exercise_data.difficulty.value,
            error=exercise_data.error.value
        )

    # Add the specified user as participant
    dataset.add_participant(user)

    return dataset

def get_error_stats(user: User, dataset_id: str | None = None) -> list[dict]:
    '''Get error stats for a user, optionally filtered by dataset.'''
    if dataset_id:
        error_stats = user.get_error_stats(dataset_id=dataset_id)['errors']
    else:
        error_stats = user.get_error_stats()['errors']
    
    return sorted(error_stats, key=lambda item: item['count'], reverse=True)

def print_error_stats(error_stats: list[dict]):
    '''Print error stats in a readable format.'''
    for i, error in enumerate(error_stats):
        error_id = error['error_id']
        error_name = SqlErrors(error_id).name if error_id in SqlErrors._value2member_map_ else 'Unknown Error'
        dav_tools.messages.message(f'{i+1}. {error_name}: {error["count"]}')

def select_errors_to_target(error_stats: list[dict]) -> list[dict]:
    '''Prompt user to select which errors to target from the error stats.'''
    indexes: list[int] = []
    while True:
        indexes_input = dav_tools.messages.ask('Enter space-separated error numbers to target (e.g. "1 3 5")')
        try:
            indexes = [int(i) for i in indexes_input.split()]
            if all(1 <= i <= len(error_stats) for i in indexes):
                break
            else:
                dav_tools.messages.error('Invalid input. Please enter valid error numbers from the list.')
        except ValueError:
            dav_tools.messages.error('Invalid input. Please enter space-separated numbers.')

    return [error_stats[i-1] for i in indexes]

def select_difficulty_levels() -> list[DifficultyLevel]:
    '''Prompt user to select which difficulty levels to target.'''
    difficulty_levels: list[DifficultyLevel] = []
    while True:
        difficulty_input = dav_tools.messages.ask('Enter space-separated difficulty levels to target (1=Easy, 2=Medium, 3=Hard, e.g. "1 3")')
        try:
            difficulty_indexes = [int(i) for i in difficulty_input.split()]
            if all(1 <= i <= 3 for i in difficulty_indexes):
                difficulty_levels = [DifficultyLevel(i) for i in difficulty_indexes]
                break
            else:
                dav_tools.messages.error('Invalid input. Please enter valid difficulty numbers (1, 2, or 3).')
        except ValueError:
            dav_tools.messages.error('Invalid input. Please enter space-separated numbers.')

    return difficulty_levels

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('user', help='Username to assign the generated exercises to')
    dav_tools.argument_parser.add_argument('-i', '--input', help='Use this dataset as a template, instead of generating a new one')
    dav_tools.argument_parser.add_argument('-o', '--output', help='Generate exercises in this dataset. If not provided, a new dataset will be created')
    dav_tools.argument_parser.add_argument('--assign-to', help='Username to assign the generated exercises to (alternative to user)')
    dav_tools.argument_parser.add_argument('--dialect', help='SQL dialect to use for generated exercises (default: postgres)', default='postgres')
    dav_tools.argument_parser.add_argument('--domain', help='Optional domain to filter exercises by')
    dav_tools.argument_parser.add_argument('--from-dataset', help='Only extract error patterns from this dataset')
    dav_tools.argument_parser.add_argument('--language', help='Language to use for generated exercises (default: en)', default='en', choices=['en', 'it'])
    dav_tools.argument_parser.parse_args()

    user = User(dav_tools.argument_parser.args.user)

    # Extract error stats for the user, optionally filtered by dataset
    sorted_error_stats = get_error_stats(user, dataset_id=dav_tools.argument_parser.args.from_dataset)

    if not sorted_error_stats:
        dav_tools.messages.error(f'No error stats found for user {user.username}. Cannot generate targeted assignment.')
        exit()

    print_error_stats(sorted_error_stats)

    # Prompt user to select which errors to target
    top_errors = select_errors_to_target(sorted_error_stats)

    # Prompt user to select difficulty levels
    difficulty_levels = select_difficulty_levels()

    errors: list[tuple[SqlErrors, DifficultyLevel]] = []

    # Create a list of (error, difficulty) tuples for the selected errors and difficulty levels
    for error in top_errors:
        for difficulty in difficulty_levels:
            errors.append((SqlErrors(error['error_id']), difficulty))

    # If --assign_to is provided, use that user instead of the one specified by 'user' argument
    assign_to = dav_tools.argument_parser.args.assign_to
    if assign_to:
        assign_to_user = User(assign_to)
    else:
        assign_to_user = user

    # If --input dataset is provided, use it as a template
    if dav_tools.argument_parser.args.input is None:
        input_dataset_str = None
        input_exercise_count = None
        title = None
        description = None
    else:
        input_dataset = Dataset(dav_tools.argument_parser.args.input)
        input_dataset_str = input_dataset.dataset_str
        input_exercise_count = len(input_dataset.list_exercises(assign_to_user))
        title = input_dataset.name
        description = input_dataset.description

    # Generate the assignment dataset and exercises
    dataset = generate_assignment(
        assign_to_user,
        errors,
        title=title,
        description=description,
        dataset_id=dav_tools.argument_parser.args.output,
        input_dataset_str=input_dataset_str,
        input_exercise_count=input_exercise_count,
        domain=dav_tools.argument_parser.args.domain,
        sql_dialect=dav_tools.argument_parser.args.dialect,
        language=dav_tools.argument_parser.args.language
    )

    dav_tools.messages.info(f'Dataset ID: {dataset.dataset_id}')