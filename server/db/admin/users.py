from typing import Any
from dav_tools import database
from .connection import db, SCHEMA
from server import gamification

import bcrypt

def _hash_password(password: str) -> str:
    '''Hash a password using bcrypt'''
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def _compare_hashed_password(password: str, hashed: str) -> bool:
    '''Compare a password with a hashed password'''
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

class User:
    '''User data model'''

    def __init__(self, username: str):
        self.username = username

        # Lazy properties
        self._badges: list[tuple[str, int]] | None = None

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, User):
            return False
        return self.username == value.username

    def __repr__(self) -> str:
        return f'User(username={self.username})'
    
    def __str__(self) -> str:
        return self.username

    # region Auth
    def exists(self) -> bool:
        '''Check if the user exists in the database'''

        query = database.sql.SQL('''
            SELECT 1
            FROM {schema}.users
            WHERE username = {username}
                AND is_active = TRUE
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'username': self.username
        })

        return len(result) > 0

    def is_admin(self) -> bool:
        '''Check if the user is an admin'''

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
            'username': self.username
        })

        if len(result) == 0:
            return False
        
        return result[0][0]

    def register_account(self, password: str, *, school: str, email: str | None = None, is_admin: bool = False) -> bool:
        '''Register a new user'''

        if self.exists():
            return False

        hashed_password = _hash_password(password)

        query = database.sql.SQL('''
            INSERT INTO {schema}.users(username, password_hash, email, school, is_admin)
            VALUES ({username}, {password_hash}, {email}, {school}, {is_admin})
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            password_hash=database.sql.Placeholder('password_hash'),
            email=database.sql.Placeholder('email'),
            school=database.sql.Placeholder('school'),
            is_admin=database.sql.Placeholder('is_admin')
        )

        db.execute(query, {
            'username': self.username,
            'password_hash': hashed_password,
            'email': email,
            'school': school,
            'is_admin': is_admin,
        })

        return True

    def delete_account(self) -> None:
        '''Delete a user'''

        query = database.sql.SQL('''
            DELETE FROM {schema}.users
            WHERE username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        db.execute(query, {
            'username': self.username
        })

    def can_login(self, password: str) -> bool:
        '''Check if a user can log in with the given credentials'''

        query = database.sql.SQL('''
            SELECT password_hash
            FROM
                {schema}.users
            WHERE
                username = {username}
                AND is_active = TRUE
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'username': self.username
        })

        if not result:
            return False
        
        stored_hash = result[0][0]
        return _compare_hashed_password(password, stored_hash)

    def change_password(self, new_password: str) -> bool:
        '''Change the password for a user'''

        if not self.exists():
            return False

        hashed_new_password = _hash_password(new_password)

        query = database.sql.SQL('''
            UPDATE {schema}.users
            SET password_hash = {new_password}
            WHERE username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            new_password=database.sql.Placeholder('new_password'),
            username=database.sql.Placeholder('username')
        )

        db.execute(query, {
            'new_password': hashed_new_password,
            'username': self.username
        })

        return True
    # endregion

    # region Badges
    def has_badge(self, badge: str, rank: int = 1) -> bool:
        '''Check if the user has a specific badge'''

        if self._badges is None:
            query = database.sql.SQL(
                '''
                    SELECT
                        badge,
                        rank
                    FROM {schema}.badges
                    WHERE
                        username = {username}
                        AND rank = {rank}
                '''
            ).format(
                schema=database.sql.Identifier(SCHEMA),
                username=database.sql.Placeholder('username'),
                rank=database.sql.Placeholder('rank')
            )

            result = db.execute_and_fetch(query, {
                'username': self.username,
                'rank': rank
            })

            self._badges = [(row[0], row[1]) for row in result]
        
        return (badge, rank) in self._badges

    def count_days_active(self) -> int:
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
            'username': self.username
        })

        return result[0][0] if result else 0

    def count_all_datasets_joined(self) -> int:
        '''Get the amount of datasets a user has joined'''

        query = database.sql.SQL(
        '''
            SELECT
                COUNT(*)
            FROM
                {schema}.dataset_members
            WHERE
                username = {username}
                AND is_teacher = FALSE
                AND dataset_id ~ '^[[:alnum:]]+$';      -- Don't count special datasets
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'username': self.username
        })

        return result[0][0] if result else 0

    def count_help_usage(self) -> int:
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
            'username': self.username
        })

        return result[0][0] if result else 0

    def _add_badge(self, badge: str, rank: int = 1) -> bool:
        '''Add a badge to a user'''

        if self.has_badge(badge, rank):
            return False

        query = database.sql.SQL('''
            INSERT INTO {schema}.badges (username, badge, rank)
            VALUES ({username}, {badge}, {rank})
            ON CONFLICT (username, badge, rank) DO NOTHING
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            badge=database.sql.Placeholder('badge'),
            rank=database.sql.Placeholder('rank')
        )

        db.execute(query, {
            'username': self.username,
            'badge': badge,
            'rank': rank
        })

        if self._badges is not None:
            self._badges.append((badge, rank))

        return True

    def count_feedbacks(self) -> int:
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
            'username': self.username
        })

        return result[0][0] if result else 0

    def get_coins(self) -> int:
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
            'username': self.username
        })

        if len(result) == 0:
            return 0
        
        return result[0][0]

    def can_afford(self, cost: gamification.Reward) -> bool:
        '''Check if the user can afford an action with the given cost'''

        coins = self.get_coins()
        return coins >= abs(cost.coins)

    def get_info(self) -> dict:
        '''
            Retrieve using a single query all relevant user info
        
            Returns a dictionary with keys:
            - username
            - is_admin
            - xp
            - coins
        '''

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
            'username': self.username
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

    def count_exercises_solved(self) -> int:
        '''Get the amount of exercises solved by the user'''

        query = database.sql.SQL('''
            SELECT
                COUNT(DISTINCT qb.exercise_id)
            FROM
                {schema}.exercise_solutions es
                JOIN {schema}.queries q ON q.id = es.id
                JOIN {schema}.query_batches qb ON qb.id = q.batch_id
            WHERE
                qb.username = {username}
                AND es.is_correct = TRUE
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'username': self.username
        })

        return result[0][0] if result else 0

    def count_unique_queries(self) -> int:
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
            'username': self.username
        })

        return result[0][0]

    def add_rewards(self, *, rewards: list[gamification.Reward], badges: list[gamification.Reward]) -> None:
        '''Add rewards to a user'''

        for badge in badges:
            self._add_badge(badge.reason)

        total_reward = gamification.Reward('')
        for r in rewards + badges:
            total_reward += r

        if total_reward.is_empty():
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
            'coins': total_reward.coins,
            'experience': total_reward.experience,
            'username': self.username
        })
    
    def count_own_exercises_with_at_least_one_own_query(self) -> int:
        '''Get the count of exercises created by a user that have at least one execution by the same user'''

        query = database.sql.SQL('''
            SELECT COUNT(*)
            FROM {schema}.exercises e
            WHERE e.created_by = {username}
            AND EXISTS (
                SELECT 1
                FROM {schema}.query_batches qb
                WHERE qb.exercise_id = e.id
                AND qb.username = {username}
            )
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'username': self.username
        })

        return result[0][0] if result else 0

    def count_exercises_created(self) -> int:
        '''Get the number of exercises created by a user'''

        query = database.sql.SQL('''
            SELECT COUNT(*)
            FROM {schema}.exercises
            WHERE created_by = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'username': self.username
        })

        return result[0][0] if result else 0
    # endregion

    # region Stats

    #######################################################################
    #                           USER STATS                                #
    # ------------------------------------------------------------------- #
    # dataset | exercise  | teacher   | result                            #
    # --------|-----------|-----------|---------------------------------- #
    # ❌      | ❌        | any       | stats for single user             #
    # ❌      | ✅        | any       | shouldn't happen (fallback to {}) #
    # ✅      | ❌        | ❌        | class stats for single student    #
    # ✅      | ❌        | ✅        | class stats for ALL students      #
    # ✅      | ✅        | ❌        | exercise stats for single student #
    # ✅      | ✅        | ✅        | exercise stats for ALL students   #
    #######################################################################

    def get_query_stats(self, *, dataset_id: str | None = None, exercise_id: int | None = None, is_teacher: bool = False) -> dict:
        '''
            Get, for each query type, the amount of queries run by the user.
            Supports different levels of granularity.

            Parameters:
            - username: The username of the user to get stats for.
            - dataset_id: The ID of the class to get stats for (optional). If provided, will return stats only for the class.
            - exercise_id: The ID of the exercise to get stats for (optional). If provided, will return stats only for the exercise.
            - is_teacher: Whether the user is a teacher. If True, will return stats for all students in the class or exercise, else will return stats only for the current user.
        '''

        if dataset_id is None and exercise_id is not None:
            return {}  # fallback case

        if dataset_id is None:
            # Global stats
            query = database.sql.SQL(
            '''
                SELECT
                    query_type,
                    queries,
                    queries_d,
                    queries_success
                FROM
                    {schema}.v_stats_queries_by_user
                WHERE
                    username = {username}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                username=database.sql.Placeholder('username')
            )
            params = {'username': self.username}

        elif exercise_id is None:
            if is_teacher:
                # Class-wide stats for teacher (excluding other teachers)
                query = database.sql.SQL(
                '''
                    SELECT
                        query_type,
                        SUM(queries),
                        SUM(queries_d),
                        SUM(queries_success)
                    FROM
                        {schema}.v_stats_queries_by_exercise
                    WHERE
                        dataset_id = {dataset_id}
                        AND is_teacher = FALSE
                    GROUP BY
                        query_type
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id')
                )
                params = {'dataset_id': dataset_id}
            else:
                # Class stats for student
                query = database.sql.SQL(
                '''
                    SELECT
                        query_type,
                        queries,
                        queries_d,
                        queries_success
                    FROM
                        {schema}.v_stats_queries_by_exercise
                    WHERE
                        dataset_id = {dataset_id}
                        AND username = {username}
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'dataset_id': dataset_id, 'username': self.username}

        else:
            if is_teacher:
                # Exercise stats for all students
                query = database.sql.SQL(
                '''
                    SELECT
                        query_type,
                        SUM(queries),
                        SUM(queries_d),
                        SUM(queries_success)
                    FROM
                        {schema}.v_stats_queries_by_exercise
                    WHERE
                        exercise_id = {exercise_id}
                        AND is_teacher = FALSE
                    GROUP BY
                        query_type
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id')
                )
                params = {'exercise_id': exercise_id}
            else:
                # Exercise stats for a student
                query = database.sql.SQL(
                '''
                    SELECT
                        query_type,
                        queries,
                        queries_d,
                        queries_success
                    FROM
                        {schema}.v_stats_queries_by_exercise
                    WHERE
                        exercise_id = {exercise_id}
                        AND username = {username}
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'exercise_id': exercise_id, 'username': self.username}

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
                    'count': int(row[1]),
                    'count_d': int(row[2]),
                    'success': int(row[3])
                } for row in result
            ],
        }

    def get_message_stats(self, *, dataset_id: str | None = None, exercise_id: int | None = None, is_teacher: bool = False) -> dict:
        '''Get statistics about chat interactions for a user'''

        if dataset_id is None and exercise_id is not None:
            return {}  # fallback case

        if dataset_id is None:
            # Global stats
            query = database.sql.SQL(
            '''
                SELECT
                    messages,
                    messages_select,
                    messages_success,
                    messages_feedback
                FROM
                    {schema}.v_stats_messages_by_user
                WHERE
                    username = {username}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                username=database.sql.Placeholder('username')
            )
            params = {'username': self.username}

        elif exercise_id is None:
            if is_teacher:
                query = database.sql.SQL(
                '''
                    SELECT
                        SUM(messages),
                        SUM(messages_select),
                        SUM(messages_success),
                        SUM(messages_feedback)
                    FROM
                    {schema}.v_stats_messages_by_exercise
                    WHERE dataset_id = {dataset_id}
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id')
                )
                params = {'dataset_id': dataset_id}
            else:
                query = database.sql.SQL(
                '''
                    SELECT
                        SUM(messages),
                        SUM(messages_select),
                        SUM(messages_success),
                        SUM(messages_feedback)
                    FROM
                        {schema}.v_stats_messages_by_exercise
                    WHERE
                        dataset_id = {dataset_id}
                        AND username = {username}
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'dataset_id': dataset_id, 'username': self.username}

        else:
            if is_teacher:
                query = database.sql.SQL(
                '''
                    SELECT
                        SUM(messages),
                        SUM(messages_select),
                        SUM(messages_success),
                        SUM(messages_feedback)
                    FROM
                        {schema}.v_stats_messages_by_exercise
                    WHERE
                        exercise_id = {exercise_id}
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id')
                )
                params = {'exercise_id': exercise_id}
            else:
                query = database.sql.SQL(
                '''
                    SELECT
                        messages,
                        messages_select,
                        messages_success,
                        messages_feedback
                    FROM
                        {schema}.v_stats_messages_by_exercise
                    WHERE
                        exercise_id = {exercise_id}
                        AND username = {username}
                ''').format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'exercise_id': exercise_id, 'username': self.username}

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
            'messages': int(result[0] or 0),
            'messages_select': int(result[1] or 0),
            'messages_success': int(result[2] or 0),
            'messages_feedback': int(result[3] or 0),
        }

    def get_error_stats(self, *, dataset_id: str | None = None, exercise_id: int | None = None, is_teacher: bool = False) -> dict:
        '''Get statistics about errors for a user'''

        if dataset_id is None and exercise_id is not None:
            return {}  # fallback case
        
        if dataset_id is None:
            # Global stats
            query = database.sql.SQL(
                '''
                    SELECT
                        error_id,
                        SUM(occurrences) AS occurrences
                    FROM
                        {schema}.v_stats_errors_by_user
                    WHERE
                        username = {username}
                    GROUP BY
                        error_id
                '''
            ).format(
                schema=database.sql.Identifier(SCHEMA),
                username=database.sql.Placeholder('username')
            )
            params = {'username': self.username}

        elif exercise_id is None:
            if is_teacher:
                # Class-wide stats for teacher (excluding other teachers)
                query = database.sql.SQL(
                    '''
                        SELECT
                            error_id,
                            SUM(occurrences) AS occurrences
                        FROM
                            {schema}.v_stats_errors_by_exercise
                        WHERE
                            dataset_id = {dataset_id}
                            AND is_teacher = FALSE
                        GROUP BY
                            error_id
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id')
                )
                params = {'dataset_id': dataset_id}
            else:
                # Class stats for student
                query = database.sql.SQL(
                    '''
                        SELECT
                            error_id,
                            SUM(occurrences) AS occurrences
                        FROM
                            {schema}.v_stats_errors_by_exercise
                        WHERE
                            dataset_id = {dataset_id}
                            AND username = {username}
                        GROUP BY
                            error_id
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'dataset_id': dataset_id, 'username': self.username}

        else:
            if is_teacher:
                # Exercise stats for all students
                query = database.sql.SQL(
                    '''
                        SELECT
                            error_id,
                            SUM(occurrences) AS occurrences
                        FROM
                            {schema}.v_stats_errors_by_exercise
                        WHERE
                            exercise_id = {exercise_id}
                            AND is_teacher = FALSE
                        GROUP BY
                            error_id
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id')
                )
                params = {'exercise_id': exercise_id}
            else:
                # Exercise stats for a student
                query = database.sql.SQL(
                    '''
                        SELECT
                            error_id,
                            SUM(occurrences) AS occurrences
                        FROM
                            {schema}.v_stats_errors_by_exercise
                        WHERE
                            exercise_id = {exercise_id}
                            AND username = {username}
                        GROUP BY
                            error_id
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'exercise_id': exercise_id, 'username': self.username}

        result = db.execute_and_fetch(query, params)

        timeline = self.get_error_timeline(dataset_id=dataset_id, exercise_id=exercise_id, is_teacher=is_teacher)
        return {
            'errors': [
                {
                    'error_id': row[0],
                    'count': int(row[1]),                
                } for row in result
            ],
            'timeline': timeline,
        }

    def get_error_timeline(self, *, dataset_id: str | None = None, exercise_id: int | None = None, is_teacher: bool = False) -> list[dict]:
        '''Get a timeline of errors for a user'''

        if dataset_id is None and exercise_id is not None:
            return []  # fallback case
        
        if dataset_id is None:
            # Global stats
            query = database.sql.SQL(
                '''
                    SELECT
                        day,
                        error_id,
                        occurrences
                    FROM
                        {schema}.v_stats_error_timeline_by_user
                    WHERE
                        username = {username}
                    ORDER BY
                        day ASC
                '''
            ).format(
                schema=database.sql.Identifier(SCHEMA),
                username=database.sql.Placeholder('username')
            )
            params = {'username': self.username}
        elif exercise_id is None:
            if is_teacher:
                # Dataset-wide stats for teacher (excluding other teachers)
                query = database.sql.SQL(
                    '''
                        SELECT
                            day,
                            error_id,
                            SUM(occurrences) AS occurrences
                        FROM
                            {schema}.v_stats_error_timeline_by_exercise
                        WHERE
                            dataset_id = {dataset_id}
                            AND is_teacher = FALSE
                        GROUP BY
                            day, error_id
                        ORDER BY
                            day ASC
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id')
                )
                params = {'dataset_id': dataset_id}
            else:
                # Dataset stats for student
                query = database.sql.SQL(
                    '''
                        SELECT
                            day,
                            error_id,
                            SUM(occurrences) AS occurrences 
                        FROM
                            {schema}.v_stats_error_timeline_by_exercise
                        WHERE
                            dataset_id = {dataset_id}
                            AND username = {username}
                        GROUP BY
                            day, error_id
                        ORDER BY
                            day ASC
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    dataset_id=database.sql.Placeholder('dataset_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'dataset_id': dataset_id, 'username': self.username}
        else:
            if is_teacher:
                # Exercise stats for all students
                query = database.sql.SQL(
                    '''
                        SELECT
                            day,
                            error_id,
                            SUM(occurrences) AS occurrences
                        FROM
                            {schema}.v_stats_error_timeline_by_exercise
                        WHERE
                            exercise_id = {exercise_id}
                            AND is_teacher = FALSE
                        GROUP BY
                            day, error_id
                        ORDER BY
                            day ASC
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id')
                )
                params = {'exercise_id': exercise_id}
            else:
                # Exercise stats for a student
                query = database.sql.SQL(
                    '''
                        SELECT
                            day,
                            error_id,
                            SUM(occurrences) AS occurrences
                        FROM
                            {schema}.v_stats_error_timeline_by_exercise
                        WHERE
                            exercise_id = {exercise_id}
                            AND username = {username}
                        GROUP BY
                            day, error_id
                        ORDER BY
                            day ASC
                    '''
                ).format(
                    schema=database.sql.Identifier(SCHEMA),
                    exercise_id=database.sql.Placeholder('exercise_id'),
                    username=database.sql.Placeholder('username')
                )
                params = {'exercise_id': exercise_id, 'username': self.username}

        result = db.execute_and_fetch(query, params)

        return [
            {
                'date': row[0],
                'error_id': int(row[1]),
                'count': int(row[2]),
            } for row in result
        ]            
    # endregion

    # region Datasets
    def list_datasets(self) -> list[dict[str, Any]]:
        '''
            Get all datasets a user belongs to

            Returns:
            A list of datasets with the following fields:
            - dataset_id: The ID of the dataset
            - title: The name of the dataset
            - is_teacher: Whether the user is a teacher in the dataset
            - participants: The number of participants in the dataset
            - exercises: The number of exercises in the dataset
            - queries_user: The number of queries run by the user
            - queries_students: The number of queries run by students (0 if the user is not a teacher)
        
        '''

        query = database.sql.SQL(
        '''
            SELECT
                id,
                name,
                is_teacher,
                participants,
                exercises,
                queries_user,
                queries_students
            FROM {schema}.v_dataset_list
            WHERE username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'username': self.username
        })

        return [{
            'dataset_id': row[0],
            'title': row[1],
            'is_teacher': bool(row[2]),
            'participants': int(row[3]),
            'exercises': int(row[4]),
            'queries_user': int(row[5]),
            'queries_students': int(row[6])
        } for row in result]
    # endregion