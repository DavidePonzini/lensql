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
) -> None:
    '''Generate SQL assignments based on specified SQL errors and difficulty levels.'''

    assignment = sql_assignment_generator.generate_assignment(
        errors=errors,
        domain=domain,
        shuffle_exercises=False,
        naming_func=lambda error, difficulty: f'{error.name} - {difficulty.name}'
    )

    # format: 'p_250113'
    schema_name = datetime.now().strftime('p_%y%m%d')
    
    # Save dataset to the database
    dataset = Dataset.create(
        title=TITLE,
        description=random.choice(SUBTITLES),
        dataset_str=assignment.dataset.to_sql(schema_name)
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
            solutions=exercise_data.solutions,
            search_path=schema_name,
            difficulty=exercise_data.difficulty.value
        )

    # Add the specified user as participant
    dataset.add_participant(user)