import dav_tools
import sqlexercise
from sqlerrors import SqlErrors, SqlErrorCategory
from sqlexercise import DifficultyLevel
from sqlscope import Dialect
from server.db.admin import Activity, Exercise, User
from server.db.users import get_database
from datetime import datetime
from server.scripts import util

admin_user = User('lens')

def generate_assignment(
    errors: list[tuple[SqlErrors, DifficultyLevel]],
    *,
    title: str | None = None,
    description: str | None = None,
    activity_id: str | None = None,
    input_activity_str: str | None = None,
    input_exercise_count: int = 0,
    domain: str | None = None,
    dialect: Dialect = Dialect.POSTGRES,
    language: str = 'en',
) -> Activity:
    '''Generate SQL assignments based on specified SQL errors and difficulty levels.'''

    db = get_database(admin_user.username, dialect)
    db.get_connection() # Ensure we can connect to the database before proceeding

    assignment = sqlexercise.generate_assignment(
        errors=errors,
        db_host=db.hostname,
        db_port=db.port,
        db_user=db.admin_username,
        db_password='password',
        sql_dialect=dialect,
        language=language,
        dataset_str=input_activity_str,
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

    if activity_id is None:
        # Generate a new activity

        # format: 'p_250113'
        schema_name = datetime.now().strftime('p_%y%m%d')
        if input_activity_str is not None:
            activity_str = input_activity_str
        else:
            activity_str = assignment.dataset.to_sql(schema_name)
    
        # Save activity to the database
        activity = Activity.create(
            title=title,
            description=description,
            activity_str=activity_str,
            domain=domain,
            search_path=schema_name,
            dbms=dialect,
        )
    else:
        # Use existing activity
        activity = Activity(activity_id)
        

    # Add admin user as participant and set as owner
    activity.add_participant(admin_user)
    activity.set_owner_status(admin_user, True)

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
            activity_id=activity.activity_id,
            request=exercise_data.request,
            solutions=[query.sql for query in exercise_data.solutions],
            difficulty=exercise_data.difficulty.value,
            error=exercise_data.error.value
        )

    return activity

if __name__ == '__main__':
    dav_tools.argument_parser.add_argument('-i', '--input', help='Use this activity as a template, instead of generating a new one')
    dav_tools.argument_parser.add_argument('-o', '--output', help='Generate exercises in this activity. If not provided, a new activity will be created')
    dav_tools.argument_parser.add_argument('--dialect', help='SQL dialect to use for generated exercises (default: postgres)', default='postgres')
    dav_tools.argument_parser.add_argument('--domain', help='Optional domain to filter exercises by')
    dav_tools.argument_parser.add_argument('--language', help='Language to use for generated exercises (default: en)', default='en', choices=['en', 'it'])
    dav_tools.argument_parser.parse_args()

    input_activity_id = dav_tools.argument_parser.args.input
    output_activity_id = dav_tools.argument_parser.args.output
    domain = dav_tools.argument_parser.args.domain
    sql_dialect = dav_tools.argument_parser.args.dialect
    language = dav_tools.argument_parser.args.language

    util.print_taxonomy()

    # Prompt user to select which errors to target and their corresponding difficulty levels
    errors: list[tuple[SqlErrors, DifficultyLevel]] = util.select_target_errors()

    # If --input activity is provided, use it as a template
    if input_activity_id is None:
        input_activity_str = None
        input_exercise_count = 0
        title = None
        description = None
    else:
        input_activity = Activity(input_activity_id)
        input_activity_str = input_activity.activity_str
        title = input_activity.name
        description = input_activity.description

        # Only set input_exercise_count if the output activity is the same as the input activity,
        # otherwise we don't want to count existing exercises in a different activity
        if output_activity_id == input_activity_id:
            input_exercise_count = len(input_activity.list_exercises(admin_user))
        else:
            input_exercise_count = 0

    # Generate the assignment activity and exercises
    activity = generate_assignment(
        errors,
        title=title,
        description=description,
        activity_id=output_activity_id,
        input_activity_str=input_activity_str,
        input_exercise_count=input_exercise_count,
        domain=domain,
        dialect=sql_dialect,
        language=language
    )

    dav_tools.messages.info(f'Activity ID: {activity.activity_id}')
