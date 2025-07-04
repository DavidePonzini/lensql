from dav_tools import database
from .connection import db, SCHEMA


def exists(class_id: str) -> bool:
    '''Check if a class exists by its ID'''

    query = database.sql.SQL(
    '''
        SELECT COUNT(*)
        FROM {schema}.classes
        WHERE id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'class_id': class_id
    })

    return result[0][0] > 0

def get(class_id: str) -> dict:
    '''Get a class by its ID'''

    query = database.sql.SQL(
    '''
        SELECT
            name,
            dataset
        FROM {schema}.classes
        WHERE id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'class_id': class_id
    })

    if len(result) == 0:
        raise ValueError(f'Class with ID {class_id} does not exist')
    
    return {
        'title': result[0][0],
        'dataset': result[0][1]
    }

def list_classes(username: str) -> list[dict]:
    '''Get all classes a user belongs to'''

    query = database.sql.SQL(
    '''
        SELECT
            c.id,
            c.name,
            cm.is_teacher,

            -- total number of students in the class
            (
                SELECT COUNT(*)
                FROM {schema}.class_members cm2
                WHERE cm2.class_id = c.id AND cm2.is_teacher = FALSE
            ) AS participants,

            -- total number of exercises in the class
            (
                SELECT COUNT(*)
                FROM {schema}.exercises e2
                WHERE e2.class_id = c.id
            ) AS exercises,

            -- count of queries:
            -- if the user is a teacher → count queries from students only
            -- else → only count user's own queries
            COUNT(q.*) FILTER (
                WHERE
                    qb.username IS NOT NULL
                    AND (
                        NOT cm.is_teacher AND qb.username = cm.username
                        OR cm.is_teacher AND qb.username IN (
                            SELECT username
                            FROM {schema}.class_members
                            WHERE class_id = c.id AND is_teacher = FALSE
                        )
                    )
            ) AS queries

        FROM {schema}.classes c
        JOIN {schema}.class_members cm ON cm.class_id = c.id

        LEFT JOIN {schema}.exercises e ON e.class_id = c.id
        LEFT JOIN {schema}.query_batches qb ON qb.exercise_id = e.id
        LEFT JOIN {schema}.queries q ON q.batch_id = qb.id

        WHERE cm.username = {username}

        GROUP BY c.id, c.name, cm.is_teacher, cm.joined_ts
        ORDER BY cm.joined_ts DESC, c.name;
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return [{
        'class_id': row[0],
        'title': row[1],
        'is_teacher': row[2],
        'participants': row[3],
        'exercises': row[4],
        'queries': row[5]
    } for row in result]

def create(title: str, dataset: str) -> str:
    '''Create a new class'''

    result = db.insert(SCHEMA, 'classes', {
        'name': title,
        'dataset': dataset
    }, ['id'])

    return result[0][0]

def update(class_id: str, title: str, dataset: str) -> None:
    '''Update an existing class'''

    query = database.sql.SQL(
    '''
        UPDATE {schema}.classes
        SET
            name = {title},
            dataset = {dataset}
        WHERE id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        title=database.sql.Placeholder('title'),
        class_id=database.sql.Placeholder('class_id'),
        dataset=database.sql.Placeholder('dataset')
    )

    db.execute(query, {
        'title': title,
        'class_id': class_id,
        'dataset': dataset
    })

def delete(class_id: str) -> None:
    '''Delete a class by its ID'''

    query = database.sql.SQL(
    '''
        DELETE FROM {schema}.classes
        WHERE id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    db.execute(query, {
        'class_id': class_id
    })

def has_teacher(username: str, class_id: str) -> bool:
    '''Check if a user is a teacher of a class'''

    query = database.sql.SQL(
    '''
        SELECT
            is_teacher
        FROM
            {schema}.class_members
        WHERE
            username = {username}
            AND class_id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'username': username,
        'class_id': class_id
    })

    if len(result) == 0:
        return False
    
    return result[0][0]

def join(username: str, class_id: str) -> None:
    '''Join a class as a student'''

    db.insert(SCHEMA, 'class_members', {
        'username': username,
        'class_id': class_id,
        })

def can_leave(username: str, class_id: str) -> bool:
    '''Check if a user can leave a class. User cannot leave if they are a teacher and the class has at least one exercise, one student or one query assigned to it.'''

    if not has_teacher(username, class_id):
        return True

    # Check if there are any exercises assigned to the class
    query = database.sql.SQL(
    '''
        SELECT COUNT(*)
        FROM {schema}.exercises
        WHERE class_id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'class_id': class_id
    })

    if result[0][0] > 0:
        return False
    
    # Check if there are any students in the class
    query = database.sql.SQL(
    '''
        SELECT COUNT(*)
        FROM {schema}.class_members
        WHERE class_id = {class_id} AND is_teacher = FALSE
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'class_id': class_id
    })

    if result[0][0] > 0:
        return False
    
    # Check if there are any queries assigned to the class
    query = database.sql.SQL(
    '''
        SELECT COUNT(*)
        FROM {schema}.query_batches qb
        JOIN {schema}.exercises e ON qb.exercise_id = e.id
        WHERE e.class_id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'class_id': class_id
    })

    if result[0][0] > 0:
        return False
    
    return True

def leave(username: str, class_id: str) -> bool:
    '''Leave a class. User cannot leave if they are a teacher and the class has at least one exercise, one student or one query assigned to it.'''

    if not can_leave(username, class_id):
        return False

    query = database.sql.SQL(
    '''
        DELETE FROM {schema}.class_members
        WHERE
            username = {username}
            AND class_id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        class_id=database.sql.Placeholder('class_id')
    )

    db.execute(query, {
        'username': username,
        'class_id': class_id
    })

    return True

def list_exercises(username: str, class_id: str) -> list[dict]:
    '''Get all exercises assigned to a user in a class'''

    query = database.sql.SQL(
    '''
        SELECT
            e.id,
            e.title,
            e.request,
            a.submission_ts,
            e.is_ai_generated
        FROM
            {schema}.assigned_to a
            JOIN {schema}.exercises e ON a.exercise_id = e.id
        WHERE
            a.username = {username}
            AND e.class_code = {class_id}
        ORDER BY
            CASE WHEN a.submission_ts IS NULL THEN 0 ELSE 1 END,
            e.title,
            e.id
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        class_id=database.sql.Placeholder('class_id')
    )

def list_all_exercises(username: str) -> list[dict]:
    '''Get all exercises assigned to a user'''

def get_students(username: str, class_id: str) -> list[dict]:
    '''Get all students in a class in which the user is a teacher'''

def has_participant(username: str, class_id: str) -> bool:
    '''Check if a user is a participant of a class'''

    query = database.sql.SQL(
    '''
        SELECT COUNT(*)
        FROM {schema}.class_members
        WHERE
            username = {username}
            AND class_id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'username': username,
        'class_id': class_id
    })

    return result[0][0] > 0

def make_teacher(username: str, class_id: str) -> None:
    '''Make a user a teacher of a class'''

    if not has_participant(username, class_id):
        raise ValueError(f'User {username} is not a participant of class {class_id}')
    
    query = database.sql.SQL(
    '''
        UPDATE {schema}.class_members
        SET is_teacher = TRUE
        WHERE
            username = {username}
            AND class_id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        class_id=database.sql.Placeholder('class_id')
    )

    db.execute(query, {
        'username': username,
        'class_id': class_id
    })

def remove_teacher(username: str, class_id: str) -> None:
    '''Remove a user as a teacher of a class.'''

    if not has_participant(username, class_id):
        raise ValueError(f'User {username} is not a participant of class {class_id}')
    
    query = database.sql.SQL(
    '''
        UPDATE {schema}.class_members
        SET is_teacher = FALSE
        WHERE
            username = {username}
            AND class_id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        class_id=database.sql.Placeholder('class_id')
    )

    db.execute(query, {
        'username': username,
        'class_id': class_id
    })
    

def get_members(class_id: str) -> list[dict]:
    '''Get all members of a class, along with their teacher status'''

    query = database.sql.SQL(
    '''
        SELECT
            cm.username,
            cm.is_teacher
        FROM
            {schema}.class_members cm
        WHERE
            cm.class_id = {class_id}
        ORDER BY
            cm.username
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'class_id': class_id
    })

    return [{
        'username': row[0],
        'is_teacher': row[1]
    } for row in result]

def get_dataset(class_id: int) -> str:
    '''Get the dataset for a given exercise ID'''

    query = database.sql.SQL(
        '''
        SELECT dataset
        FROM {schema}.classes
        WHERE id = {class_id}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        class_id=database.sql.Placeholder('class_id')
    )

    result = db.execute_and_fetch(query, {
        'class_id': class_id
    })

    if len(result) == 0:
        return '-- No dataset provided'

    return result[0][0]















    # query = database.sql.SQL(
    # '''
    #     SELECT
    #         e.id,
    #         e.title,
    #         e.request,
    #         a.submission_ts,
    #         e.is_ai_generated
    #     FROM
    #         {schema}.assigned_to a
    #         JOIN {schema}.exercises e ON a.exercise_id = e.id
    #     WHERE
    #         username = {username}
    #     ORDER BY
    #         CASE WHEN a.submission_ts IS NULL THEN 0 ELSE 1 END,
    #         e.title,
    #         e.id
    # ''').format(
    #     schema=database.sql.Identifier(SCHEMA),
    #     username=database.sql.Placeholder('username')
    # )

    # result = db.execute_and_fetch(query, {
    #     'username': username
    # })

    # return [
    #     {
    #         'id': row[0],
    #         'title': row[1],
    #         'request': row[2],
    #         'submission_ts': row[3],
    #         'is_ai_generated': row[4],
    #         'learning_objectives': get_learning_objectives(row[0])
    #     }
    #     for row in result
    # ]

def submit(username: str, exercise_id: int) -> None:
    '''Submit an assignment'''

    query = database.sql.SQL(
    '''
        UPDATE {schema}.assigned_to
        SET submission_ts = NOW()
        WHERE
            username = {username}
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

def unsubmit(username: str, exercise_id: int) -> None:
    '''Unsubmit an assignment'''

    query = database.sql.SQL(
    '''
        UPDATE {schema}.assigned_to
        SET submission_ts = NULL
        WHERE
            username = {username}
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

def get_students(teacher: str, exercise_id: int) -> dict:
    '''Get whether each student of this teacher is assigned to the given exercise'''

    query = database.sql.SQL(
    '''
        SELECT
            t.student AS student,
            (a.exercise_id IS NOT NULL) AS is_assigned
        FROM
            {schema}.teaches t
        LEFT JOIN
            {schema}.assigned_to a ON a.username = t.student AND a.exercise_id = {exercise_id}
        WHERE
            t.teacher = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        exercise_id=database.sql.Placeholder('exercise_id'),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'exercise_id': exercise_id,
        'username': teacher
    })

    return [{
        'username': row[0],
        'is_assigned': row[1]
    } for row in result]

def get_learning_objectives(exercise_id: int) -> list:
    '''Get the learning objectives of an exercise'''

    query = database.sql.SQL(
    '''
        SELECT
            lo.objective,
            lo.description
        FROM
            {schema}.learning_objectives lo
            JOIN {schema}.has_learning_objective hlo ON lo.objective = hlo.objective
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