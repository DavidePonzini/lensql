from dav_tools import database
from .connection import db, SCHEMA


def get_class(exercise_id: int) -> str:
    '''Get the class ID for a given exercise ID'''

    query = database.sql.SQL(
        '''
        SELECT class_id
        FROM {schema}.exercises
        WHERE id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id
    })

    if len(result) == 0:
        return None

    return result[0][0]

def is_solved(exercise_id: int, username: str) -> bool:
    '''Check if an exercise has been solved by a user'''

    query = database.sql.SQL('''
        SELECT EXISTS (
            SELECT 1
            FROM {schema}.exercise_solutions
            WHERE
                exercise_id = {exercise_id}
                AND username = {username}
                AND is_correct = TRUE
        )
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id'),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id,
        'username': username
    })

    return result[0][0] if result else False

def get_from_class(username: str, class_id: str, include_hidden: bool = False) -> list[dict]:
    '''Get all exercises assigned to a class'''

    if include_hidden:
        query = database.sql.SQL(
        '''
            SELECT
                e.id,
                e.title,
                e.request,
                e.is_ai_generated,
                e.is_hidden,
                es.username IS NOT NULL AS submitted
            FROM
                {schema}.exercises e
                LEFT JOIN {schema}.exercise_submissions es ON e.id = es.exercise_id AND es.username = {username}
            WHERE
                e.class_id = {class_id}
            ORDER BY
                e.title,
                e.id
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            class_id=database.sql.Placeholder('class_id'),
            username=database.sql.Placeholder('username'),
        )
    else:
        query = database.sql.SQL(
        '''
            SELECT
                e.id,
                e.title,
                e.request,
                e.is_ai_generated,
                FALSE AS is_hidden,
                es.username IS NOT NULL AS submitted
            FROM
                {schema}.exercises e
                LEFT JOIN {schema}.exercise_submissions es ON e.id = es.exercise_id AND es.username = {username}
            WHERE
                e.class_id = {class_id}
                AND e.is_hidden = FALSE
            ORDER BY
                e.title,
                e.id
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            class_id=database.sql.Placeholder('class_id'),
            username=database.sql.Placeholder('username'),
        )

    result = db.execute_and_fetch(query, {
        'class_id': class_id,
        'username': username,
    })

    return [
        {
            'exercise_id': row[0],
            'title': row[1],
            'request': row[2],
            'is_ai_generated': row[3],
            'is_hidden': row[4],
            'submitted': row[5],
            'learning_objectives': get_learning_objectives(row[0]),
        }
        for row in result
    ]

def get_data(exercise_id: int, username: str) -> dict:
    '''Get the exercise for a given ID, if the user is assigned to it'''

    query = database.sql.SQL(
    '''
        SELECT
            e.title,
            e.request,
            e.solution,
            e.class_id
        FROM
            {schema}.exercises e
            JOIN {schema}.classes c ON e.class_id = c.id
            JOIN {schema}.class_members cm ON c.id = cm.class_id
        WHERE
            e.id = {exercise_id}
            AND cm.username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id'),
        username=database.sql.Placeholder('username'),
    )
    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id,
        'username': username,
    })
    if len(result) == 0:
        return None
    
    result = result[0]

    return {
        'title': result[0],
        'request': result[1],
        'solution': result[2],
        'class_id': result[3],
    }

def create(title: str, *, class_id: str, request: str, solution: str | None = None, is_ai_generated: bool = False) -> int:
    '''Create a new exercise'''

    result = db.insert(SCHEMA, 'exercises', {
        'title': title,
        'class_id': class_id,
        'request': request,
        'solution': solution,
        'is_ai_generated': is_ai_generated
    }, ['id'])

    exercise_id = result[0][0]

    return exercise_id

def update(exercise_id: int, title: str, request: str, solution: str | None) -> None:
    '''Update an existing exercise'''

    query = database.sql.SQL('''
        UPDATE {schema}.exercises
        SET title = {title},
            request = {request},
            solution = {solution}
        WHERE id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        title=database.sql.Placeholder('title'),
        request=database.sql.Placeholder('request'),
        solution=database.sql.Placeholder('solution'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )
    db.execute(query, {
        'title': title,
        'request': request,
        'solution': solution,
        'exercise_id': exercise_id
    })

def delete(exercise_id: int) -> bool:
    '''Delete an exercise'''

    try:
        query = database.sql.SQL('''
            DELETE FROM {schema}.exercises
            WHERE id = {exercise_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id')
        )
        db.execute(query, {
            'exercise_id': exercise_id
        })

        return True
    except Exception:
        return False

def set_learning_objective(exercise_id: int, objective: str) -> None:
    '''Set a learning objective for an exercise'''

    query = database.sql.SQL('''
        INSERT INTO {schema}.has_learning_objective (exercise_id, objective)
        VALUES ({exercise_id}, {objective})
        ON CONFLICT (exercise_id, objective) DO NOTHING
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id'),
        objective=database.sql.Placeholder('objective')
    )

    db.execute(query, {
        'exercise_id': exercise_id,
        'objective': objective
    })

def unset_learning_objective(exercise_id: int, objective: str) -> None:
    '''Unset a learning objective for an exercise'''

    query = database.sql.SQL('''
        DELETE FROM {schema}.has_learning_objective
        WHERE exercise_id = {exercise_id}
        AND objective = {objective}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id'),
        objective=database.sql.Placeholder('objective')
    )

    db.execute(query, {
        'exercise_id': exercise_id,
        'objective': objective
    })

def list_learning_objectives(exercise_id: int) -> list[str]:
    '''List all learning objectives status for an exercise'''

    query = database.sql.SQL('''
        SELECT
            lo.objective AS objective,
            lo.description AS description,
            (hlo.objective IS NOT NULL) AS is_set
        FROM
            {schema}.learning_objectives lo
            LEFT JOIN {schema}.has_learning_objective hlo ON lo.objective = hlo.objective AND hlo.exercise_id = {exercise_id}
        ORDER BY
            lo.objective
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id
    })

    return [{
        'objective': row[0],
        'description': row[1],
        'is_set': row[2]
    } for row in result]

def get_learning_objectives(exercise_id: int) -> list[str]:
    '''Get the learning objectives for an exercise'''

    query = database.sql.SQL(
    '''
        SELECT
            hlo.objective,
            lo.description
        FROM
            {schema}.has_learning_objective hlo
            JOIN {schema}.learning_objectives lo ON hlo.objective = lo.objective
        WHERE
            hlo.exercise_id = {exercise_id}
        ORDER BY
            hlo.objective
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id
    })

    return [{
        'objective': row[0],
        'description': row[1]
    } for row in result]
                             

def get_solution(exercise_id: int) -> str | None:
    '''Get the solution for an exercise, if it exists'''

    query = database.sql.SQL('''
        SELECT solution
        FROM {schema}.exercises
        WHERE id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id
    })

    if len(result) == 0:
        return None

    return result[0][0]


def submit(username: str, exercise_id: int) -> None:
    '''Submit an exercise for a user'''

    query = database.sql.SQL('''
        INSERT INTO {schema}.exercise_submissions (username, exercise_id)
        VALUES ({username}, {exercise_id})
        ON CONFLICT (username, exercise_id) DO NOTHING
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    db.execute(query, {
        'username': username,
        'exercise_id': exercise_id
    })

def unsubmit(username: str, exercise_id: int) -> None:
    '''Unsubmit an exercise for a user'''

    query = database.sql.SQL('''
        DELETE FROM {schema}.exercise_submissions
        WHERE username = {username}
        AND exercise_id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    db.execute(query, {
        'username': username,
        'exercise_id': exercise_id
    })

def hide(exercise_id: int) -> None:
    '''Hide an exercise from students'''

    query = database.sql.SQL('''
        UPDATE {schema}.exercises
        SET is_hidden = TRUE
        WHERE id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    db.execute(query, {
        'exercise_id': exercise_id
    })

def unhide(exercise_id: int) -> None:
    '''Unhide an exercise for students'''

    query = database.sql.SQL('''
        UPDATE {schema}.exercises
        SET is_hidden = FALSE
        WHERE id = {exercise_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id')
    )

    db.execute(query, {
        'exercise_id': exercise_id
    })

def log_solution_attempt(query_id: int, username: str, exercise_id: int, is_correct: bool) -> None:
    '''Log a solution attempt for an exercise'''

    db.insert(SCHEMA, 'exercise_solutions', {
        'id': query_id,
        'exercise_id': exercise_id,
        'username': username,
        'is_correct': is_correct,
    })