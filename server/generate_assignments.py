import dav_tools
import sql_assignment_generator
from sql_assignment_generator import SqlErrors, DifficultyLevel
from server.db.admin import Dataset, Exercise, User
from datetime import datetime

admin_user = User('lens')

def generate_assignment(
    errors: list[tuple[SqlErrors, DifficultyLevel]],
    *,
    title: str | None = None,
    description: str | None = None,
    dataset_id: str | None = None,
    input_dataset_str: str | None = None,
    input_exercise_count: int = 0,
    domain: str | None = None,
    sql_dialect: str = 'postgres',
    language: str = 'en',
) -> Dataset:
    '''Generate SQL assignments based on specified SQL errors and difficulty levels.'''

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

    # Map 'postgres' to 'postgresql' for consistency with database entries
    if sql_dialect == 'postgres':
        dbms = 'postgresql'
    else:
        dbms = sql_dialect

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
            dbms=dbms,
        )
    else:
        # Use existing dataset
        dataset = Dataset(dataset_id)
        

    # Add admin user as participant and set as owner
    dataset.add_participant(admin_user)
    dataset.set_owner_status(admin_user, True)

    def get_exercise_name() -> str:
        nonlocal input_exercise_count
        input_exercise_count += 1

        if language == 'en':
            return f'Exercise {input_exercise_count}'
        if language == 'it':
            return f'Esercizio {input_exercise_count}'
        return f'Exercise {input_exercise_count}'

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

    return dataset

def print_error_list() -> None:
    for e in SqlErrors:
        dav_tools.messages.message(e.value, e.name, text_min_len=[5], additional_text_options=[[dav_tools.messages.TextFormat.Style.BOLD]])

def select_errors_to_target() -> list[tuple[SqlErrors, DifficultyLevel]]:
    '''Prompt user to select which errors to target from the error stats.'''
    selection: list[tuple[int, str]] = []
    while True:
        selection_input = dav_tools.messages.ask('Enter space-separated error numbers and difficulties to target (e.g. "1a 3b 5c")')
        try:
            selection = [(int(i[:-1]), i[-1]) for i in selection_input.split()]
            if all(1 <= i <= len(SqlErrors) and d in ['a', 'b', 'c'] for i, d in selection):
                break
            else:
                dav_tools.messages.error('Invalid input. Please enter valid error numbers and difficulties from the list.')
        except ValueError:
            dav_tools.messages.error('Invalid input. Please enter space-separated error numbers and difficulties.')

    
    result: list[tuple[SqlErrors, DifficultyLevel]] = []

    for e, d in selection:
        difficulty = DifficultyLevel(ord(d) - ord('a') + 1)
        result.append((SqlErrors(e), difficulty))
    
    return result

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('-i', '--input', help='Use this dataset as a template, instead of generating a new one')
    dav_tools.argument_parser.add_argument('-o', '--output', help='Generate exercises in this dataset. If not provided, a new dataset will be created')
    dav_tools.argument_parser.add_argument('--dialect', help='SQL dialect to use for generated exercises (default: postgres)', default='postgres')
    dav_tools.argument_parser.add_argument('--domain', help='Optional domain to filter exercises by')
    dav_tools.argument_parser.add_argument('--language', help='Language to use for generated exercises (default: en)', default='en', choices=['en', 'it'])
    dav_tools.argument_parser.parse_args()

    input_dataset_id = dav_tools.argument_parser.args.input
    output_dataset_id = dav_tools.argument_parser.args.output
    domain = dav_tools.argument_parser.args.domain
    sql_dialect = dav_tools.argument_parser.args.dialect
    language = dav_tools.argument_parser.args.language

    print_error_list()

    # Prompt user to select which errors to target and their corresponding difficulty levels
    errors: list[tuple[SqlErrors, DifficultyLevel]] = select_errors_to_target()

    # If --input dataset is provided, use it as a template
    if input_dataset_id is None:
        input_dataset_str = None
        input_exercise_count = 0
        title = None
        description = None
    else:
        input_dataset = Dataset(input_dataset_id)
        input_dataset_str = input_dataset.dataset_str
        title = input_dataset.name
        description = input_dataset.description

        # Only set input_exercise_count if the output dataset is the same as the input dataset,
        # otherwise we don't want to count existing exercises in a different dataset
        if output_dataset_id == input_dataset_id:
            input_exercise_count = len(input_dataset.list_exercises(admin_user))
        else:
            input_exercise_count = 0

    # Generate the assignment dataset and exercises
    dataset = generate_assignment(
        errors,
        title=title,
        description=description,
        dataset_id=output_dataset_id,
        input_dataset_str=input_dataset_str,
        input_exercise_count=input_exercise_count,
        domain=domain,
        sql_dialect=sql_dialect,
        language=language
    )

    dav_tools.messages.info(f'Dataset ID: {dataset.dataset_id}')
