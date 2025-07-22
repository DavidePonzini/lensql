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
    
    username, is_admin, experience, coins = result[0]

    xp = gamification.xp_to_level(experience)

    return {
        'username': username,
        'is_admin': is_admin,
        'coins': coins,
        'xp': xp['current'],
        'xp_to_next_level': xp['next'],
        'level': xp['level'],
    }

def get_unique_queries_count(username: str) -> int:
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

def add_coins(username: str, amount: int) -> None:
    '''Add coins to a user's account'''

    query = database.sql.SQL('''
        UPDATE
            {schema}.users
        SET
            coins = coins + {amount}
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        amount=database.sql.Placeholder('amount'),
        username=database.sql.Placeholder('username')
    )

    db.execute(query, {
        'amount': amount,
        'username': username
    })

def add_experience(username: str, amount: int) -> None:
    '''Add experience to a user's account'''

    query = database.sql.SQL('''
        UPDATE
            {schema}.users
        SET
            experience = experience + {amount}
        WHERE
            username = {username}
    ''').format(
        schema=database.sql.Identifier(SCHEMA),
        amount=database.sql.Placeholder('amount'),
        username=database.sql.Placeholder('username')
    )

    db.execute(query, {
        'amount': amount,
        'username': username
    })

