from dav_tools import database
from .connection import db, SCHEMA
from server import gamification

def is_admin(username: str) -> bool:
    '''Check if a user is an admin'''

    query = database.sql.SQL('''
        SELECT
            is_admin
        FROM
            {schema}.users
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    if len(result) == 0:
        return False
    
    return result[0][0]

def count_days_active(username: str) -> int:
    '''Get the amount of days a user has been active in LensQL'''

    query = database.sql.SQL('''
        SELECT
            COUNT(DISTINCT DATE(ts))
        FROM
            {schema}.query_batches
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return result[0][0] if result else 0

def count_all_classes_joined(username: str) -> int:
    '''Get the amount of classes a user has joined'''

    query = database.sql.SQL('''
        SELECT
            COUNT(*)
        FROM
            {schema}.classes_participants
        WHERE
            username = {username}
            AND is_teacher = FALSE
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return result[0][0] if result else 0

def count_help_usage(username: str) -> int:
    '''Get the amount of help messages used by a user'''

    query = database.sql.SQL('''
        SELECT
            COUNT(*)
        FROM
            {schema}.messages m
            JOIN {schema}.queries q ON q.id = m.query_id
            JOIN {schema}.query_batches qb ON qb.id = q.batch_id
        WHERE
            qb.username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return result[0][0] if result else 0

def add_badge(username: str, badge: str) -> None:
    '''Add a badge to a user'''

    query = database.sql.SQL('''
        INSERT INTO {schema}.badges (username, badge)
        VALUES ({username}, {badge})
        ON CONFLICT (username, badge) DO NOTHING
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username'),
        badge=database.sql.Placeholder('badge')
    )

    db.execute(query, {
        'username': username,
        'badge': badge
    })

def count_feedbacks(username: str) -> int:
    '''Get the amount of feedbacks provided by a user'''

    query = database.sql.SQL('''
        SELECT
            COUNT(*)
        FROM
            {schema}.messages m
            JOIN {schema}.queries q ON q.id = m.query_id
            JOIN {schema}.query_batches qb ON qb.id = q.batch_id
        WHERE
            username = {username}
            AND m.feedback IS NOT NULL
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return result[0][0] if result else 0


def get_coins(username: str) -> int:
    '''Get the amount of coins a user has'''

    query = database.sql.SQL('''
        SELECT
            coins
        FROM
            {schema}.users
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    if len(result) == 0:
        return 0
    
    return result[0][0]

def get_info(username: str) -> dict:
    '''Get general information about a user'''

    query = database.sql.SQL(
        '''
        SELECT
            u.username,
            u.is_admin,
            u.experience,
            u.coins
        FROM
            {schema}.users u
        WHERE
            u.username = {username}
        '''
    ).format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    if len(result) == 0:
        return {}
    
    result = result[0]

    return {
        'username': result[0],
        'is_admin': result[1],
        'xp': result[2],
        'coins': result[3],
    }

def count_exercises_solved(username: str) -> int:
    '''Get the amount of exercises solved by the user'''

    query = database.sql.SQL('''
        SELECT
            COUNT(DISTINCT exercise_id)
        FROM
            {schema}.exercise_solutions
        WHERE
            username = {username}
            AND is_correct = TRUE
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return result[0][0] if result else 0

def count_unique_queries(username: str) -> int:
    '''Get the amount of unique queries run by the user'''

    query = database.sql.SQL('''
        SELECT
            COUNT(DISTINCT q.query)
        FROM
            {schema}.queries q
            JOIN {schema}.query_batches qb ON qb.id = q.batch_id
        WHERE
            qb.username = {username}
            AND q.query_type <> 'BUILTIN'
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        username=database.sql.Placeholder('username')
    )

    result = db.execute_and_fetch(query, {
        'username': username
    })

    return result[0][0]


#############################################################################################################################
# USER STATS                                                                                                                #
# class | exercise  | teacher   | result                                                                                    #
# ------|-----------|-----------|------------------------------------------------------------------------------------------ #
# 0     | 0         | 0/1       | stats for single user                                                                     #
# 0     | 1         | 0/1       | N/A (should not happen, if we have an exercise, we have a class) -> fallback to nothing   #
# 1     | 0         | 0         | class stats for single student                                                            #
# 1     | 0         | 1         | class stats for ALL students                                                              #
# 1     | 1         | 0         | exercise stats for single student                                                         #
# 1     | 1         | 1         | exercise stats for ALL students                                                           #
#############################################################################################################################

def get_query_stats(username: str, *, class_id: str | None = None, exercise_id: int | None = None, is_teacher: bool = False) -> dict:
    '''
        Get, for each query type, the amount of queries run by the user.
        Supports different levels of granularity.

        Parameters:
        - username: The username of the user to get stats for.
        - class_id: The ID of the class to get stats for (optional). If provided, will return stats only for the class.
        - exercise_id: The ID of the exercise to get stats for (optional). If provided, will return stats only for the exercise.
        - is_teacher: Whether the user is a teacher. If True, will return stats for all students in the class or exercise, else will return stats only for the current user.
    '''

    if class_id is None and exercise_id is not None:
        return None  # fallback case

    if class_id is None:
        # Global stats
        query = database.sql.SQL('''
            SELECT query_type, queries, queries_d, queries_success
            FROM {schema}.v_stats_queries_by_user
            WHERE username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )
        params = {'username': username}

    elif exercise_id is None:
        if is_teacher:
            # Class-wide stats for teacher (excluding other teachers)
            query = database.sql.SQL('''
                SELECT query_type, SUM(queries), SUM(queries_d), SUM(queries_success)
                FROM {schema}.v_stats_queries_by_exercise
                WHERE class_id = {class_id}
                GROUP BY query_type
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                class_id=database.sql.Placeholder('class_id')
            )
            params = {'class_id': class_id}
        else:
            # Class stats for student
            query = database.sql.SQL('''
                SELECT query_type, queries, queries_d, queries_success
                FROM {schema}.v_stats_queries_by_exercise
                WHERE class_id = {class_id} AND username = {username}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                class_id=database.sql.Placeholder('class_id'),
                username=database.sql.Placeholder('username')
            )
            params = {'class_id': class_id, 'username': username}

    else:
        if is_teacher:
            # Exercise stats for all students
            query = database.sql.SQL('''
                SELECT query_type, SUM(queries), SUM(queries_d), SUM(queries_success)
                FROM {schema}.v_stats_queries_by_exercise
                WHERE exercise_id = {exercise_id}
                GROUP BY query_type
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                exercise_id=database.sql.Placeholder('exercise_id')
            )
            params = {'exercise_id': exercise_id}
        else:
            # Exercise stats for a student
            query = database.sql.SQL('''
                SELECT query_type, queries, queries_d, queries_success
                FROM {schema}.v_stats_queries_by_exercise
                WHERE exercise_id = {exercise_id} AND username = {username}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                exercise_id=database.sql.Placeholder('exercise_id'),
                username=database.sql.Placeholder('username')
            )
            params = {'exercise_id': exercise_id, 'username': username}

    result = db.execute_and_fetch(query, params)

    return {
        'queries': sum(row[1] for row in result),
        'queries_d': sum(row[2] for row in result),
        'queries_success': sum(row[3] for row in result),
        'queries_select': sum(row[1] for row in result if row[0] == 'SELECT'),
        'queries_success_select': sum(row[3] for row in result if row[0] == 'SELECT'),
        'query_types': [
            {
                'type': row[0],
                'count': row[1],
                'count_d': row[2],
                'success': row[3]
            } for row in result
        ],
    }

def get_message_stats(username: str, *, class_id: str | None = None, exercise_id: int | None = None, is_teacher: bool = False) -> dict:
    '''Get statistics about chat interactions for a user'''

    if class_id is None and exercise_id is not None:
        return None  # fallback case

    if class_id is None:
        # Global stats
        query = database.sql.SQL('''
            SELECT messages, messages_select, messages_success, messages_feedback
            FROM {schema}.v_stats_messages_by_user
            WHERE username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )
        params = {'username': username}

    elif exercise_id is None:
        if is_teacher:
            query = database.sql.SQL('''
                SELECT SUM(messages), SUM(messages_select), SUM(messages_success), SUM(messages_feedback)
                FROM {schema}.v_stats_messages_by_exercise
                WHERE class_id = {class_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                class_id=database.sql.Placeholder('class_id')
            )
            params = {'class_id': class_id}
        else:
            query = database.sql.SQL('''
                SELECT SUM(messages), SUM(messages_select), SUM(messages_success), SUM(messages_feedback)
                FROM {schema}.v_stats_messages_by_exercise
                WHERE class_id = {class_id} AND username = {username}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                class_id=database.sql.Placeholder('class_id'),
                username=database.sql.Placeholder('username')
            )
            params = {'class_id': class_id, 'username': username}

    else:
        if is_teacher:
            query = database.sql.SQL('''
                SELECT SUM(messages), SUM(messages_select), SUM(messages_success), SUM(messages_feedback)
                FROM {schema}.v_stats_messages_by_exercise
                WHERE exercise_id = {exercise_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                exercise_id=database.sql.Placeholder('exercise_id')
            )
            params = {'exercise_id': exercise_id}
        else:
            query = database.sql.SQL('''
                SELECT messages, messages_select, messages_success, messages_feedback
                FROM {schema}.v_stats_messages_by_exercise
                WHERE exercise_id = {exercise_id} AND username = {username}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                exercise_id=database.sql.Placeholder('exercise_id'),
                username=database.sql.Placeholder('username')
            )
            params = {'exercise_id': exercise_id, 'username': username}

    result = db.execute_and_fetch(query, params)

    if len(result) == 0:
        return {
            'messages': 0,
            'messages_select': 0,
            'messages_success': 0,
            'messages_feedback': 0,
        }
    
    result = result[0]

    return {
        'messages': result[0] or 0,
        'messages_select': result[1] or 0,
        'messages_success': result[2] or 0,
        'messages_feedback': result[3] or 0,
    }


def get_error_stats(username: str) -> dict:
    '''Get statistics about errors for a user'''

    # TODO
    return {}

def add_rewards(username: str, *, rewards: list[gamification.Reward], badges: list[gamification.Reward]) -> None:
    '''Add rewards to a user'''

    for badge in badges:
        add_badge(username, badge.reason)

    reward = gamification.Reward('')
    for r in rewards + badges:
        reward += r

    if reward.is_empty():
        return

    query = database.sql.SQL('''
        UPDATE
            {schema}.users
        SET
            coins = coins + {coins},
            experience = experience + {experience}
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        coins=database.sql.Placeholder('coins'),
        experience=database.sql.Placeholder('experience'),
        username=database.sql.Placeholder('username')
    )

    db.execute(query, {
        'coins': reward.coins,
        'experience': reward.experience,
        'username': username
    })

