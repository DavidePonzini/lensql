import json
import random
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any
from dav_tools import database
from .connection import db, SCHEMA
from sqlscope import Dialect

from .users import User
from .exercises import Exercise


@dataclass(frozen=True)
class ExerciseJSON:
    title: str
    request: str
    solutions: list[str]
    is_hidden: bool
    difficulty: int | None
    error: int | None
    learning_objectives: list[str]

@dataclass(frozen=True)
class ActivityJSON:
    title: str
    description: str
    activity_str: str
    search_path: str | None
    dbms: str | None
    domain: str | None
    exercises: list[ExerciseJSON]

class Activity:
    '''Activity-related database operations'''

    def __init__(
        self,
        activity_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        activity_str: str | None = None,
        search_path: str | None = None,
        dbms: Dialect | None = None,
        activity_start_ts: datetime | None = None,
        activity_end_ts: datetime | None = None,
    ) -> None:
        self.activity_id = activity_id

        # Lazy properties
        self._name = name
        self._description = description
        self._activity_str = activity_str
        self._search_path = search_path
        self._dbms = dbms
        self._activity_start_ts = activity_start_ts
        self._activity_end_ts = activity_end_ts

    # region Properties
    def _load_properties(self) -> None:
        '''Load all properties of the activity from the database'''

        query = database.sql.SQL(
        '''
            SELECT
                name,
                description,
                activity,
                search_path,
                activity_start_ts,
                activity_end_ts
            FROM {schema}.activities
            WHERE id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        if len(result) == 0:
            raise ValueError(f'Activity with ID {self.activity_id} does not exist.')

        self._name = result[0][0]
        self._description = result[0][1]
        self._activity_str = result[0][2] or ''
        self._search_path = result[0][3]
        self._activity_start_ts = result[0][4]
        self._activity_end_ts = result[0][5]

    @property
    def name(self) -> str:
        '''Get the name of the activity'''

        if self._name is None:
            self._load_properties()

            if self._name is None:
                raise ValueError(f'Failed to load name for activity with ID {self.activity_id}')
        return self._name
    
    @property
    def description(self) -> str:
        '''Get the description of the activity'''

        if self._description is None:
            self._load_properties()

            if self._description is None:
                raise ValueError(f'Failed to load description for activity with ID {self.activity_id}')
        
        return self._description
    
    @property
    def activity_str(self) -> str:
        '''Get the activity string'''

        if self._activity_str is None:
            self._load_properties()

            if self._activity_str is None:
                raise ValueError(f'Failed to load activity string for activity with ID {self.activity_id}')
        
        return self._activity_str
    
    @property
    def dbms(self) -> Dialect:
        '''Get the DBMS of the activity'''

        if self._dbms is None:
            query = database.sql.SQL(
            '''
                SELECT dbms
                FROM {schema}.activities
                WHERE id = {activity_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                activity_id=database.sql.Placeholder('activity_id')
            )

            result = db.execute_and_fetch(query, {
                'activity_id': self.activity_id
            })

            if len(result) == 0:
                raise ValueError(f'Activity with ID {self.activity_id} does not exist.')

            self._dbms = Dialect(result[0][0]) if result[0][0] else Dialect.POSTGRES
        
        return Dialect(self._dbms)

    @property
    def domain(self) -> str | None:
        '''Get the domain of the activity'''

        query = database.sql.SQL(
        '''
            SELECT domain
            FROM {schema}.activities
            WHERE id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        if len(result) == 0:
            raise ValueError(f'Activity with ID {self.activity_id} does not exist.')

        return result[0][0]
    
    @property
    def is_special(self) -> bool:
        '''Check if the activity is special (ID contains a special character)'''
        return not self.activity_id.isalnum()
    
    @property
    def search_path(self) -> str:
        '''Get the search path for the activity'''

        if self._search_path is None:
            self._load_properties()

            if self._search_path is None:
                raise ValueError(f'Failed to load search path for activity with ID {self.activity_id}')
        return self._search_path

    @property
    def activity_start_ts(self) -> datetime | None:
        '''Get the optional start of the activity activity window.'''

        if self._activity_start_ts is None:
            self._load_properties()
        return self._activity_start_ts

    @property
    def activity_end_ts(self) -> datetime | None:
        '''Get the optional end of the activity activity window.'''

        if self._activity_end_ts is None:
            self._load_properties()
        return self._activity_end_ts
    # endregion

    # region CRUD
    def rename_id(self, new_id: str) -> bool:
        '''Rename the primary key, cascading to memberships and exercises.'''
        query = database.sql.SQL('''
            UPDATE {schema}.activities SET id = {new_id}
            WHERE id = {activity_id}
            RETURNING id
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            new_id=database.sql.Placeholder('new_id'),
            activity_id=database.sql.Placeholder('activity_id'),
        )
        result = db.execute_and_fetch(query, {
            'new_id': new_id,
            'activity_id': self.activity_id,
        })
        if not result:
            return False
        self.activity_id = result[0][0]
        return True

    def exists(self) -> bool:
        '''Check if a activity exists by its ID'''

        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.activities
            WHERE id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        return result[0][0] > 0

    @staticmethod
    def create(
        title: str,
        description: str,
        activity_str: str,
        *,
        domain: str | None = None,
        activity_id: str | None = None,
        search_path: str | None = None,
        dbms: Dialect,
        activity_start_ts: datetime | None = None,
        activity_end_ts: datetime | None = None,
    ) -> 'Activity':
        '''Create a new activity, optionally with a specified ID'''

        if activity_id is not None:
            result = db.insert(SCHEMA, 'activities', {
                'id': activity_id,
                'name': title,
                'description': description,
                'activity': activity_str.strip() or None,
                'domain': domain,
                'search_path': search_path,
                'dbms': dbms.value,
                'activity_start_ts': activity_start_ts,
                'activity_end_ts': activity_end_ts,
            }, ['id'])
        else:
            result = db.insert(SCHEMA, 'activities', {
                'name': title,
                'description': description,
                'activity': activity_str.strip() or None,
                'domain': domain,
                'search_path': search_path,
                'dbms': dbms.value,
                'activity_start_ts': activity_start_ts,
                'activity_end_ts': activity_end_ts,
            }, ['id'])

        assert result is not None and len(result) > 0, 'Failed to create activity'

        activity_id = result[0][0]

        return Activity(
            activity_id,
            name=title,
            description=description,
            activity_str=activity_str,
            search_path=search_path,
            dbms=dbms,
            activity_start_ts=activity_start_ts,
            activity_end_ts=activity_end_ts,
        )

    def dump(self) -> ActivityJSON:
        '''Dump a activity and its exercises to a JSON-serializable structure.'''

        activity_query = database.sql.SQL(
        '''
            SELECT
                name,
                description,
                activity,
                search_path,
                dbms,
                domain
            FROM {schema}.activities
            WHERE id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )
        activity_rows = db.execute_and_fetch(activity_query, {
            'activity_id': self.activity_id
        })
        if not activity_rows:
            raise ValueError(f'Activity with ID {self.activity_id} does not exist.')

        exercise_query = database.sql.SQL(
        '''
            SELECT
                e.title,
                e.request,
                e.solutions,
                e.is_hidden,
                e.generation_difficulty,
                e.generation_error,
                COALESCE(
                    ARRAY(
                        SELECT hlo.objective_id
                        FROM {schema}.has_learning_objective hlo
                        WHERE hlo.exercise_id = e.id
                        ORDER BY hlo.objective_id
                    ),
                    ARRAY[]::text[]
                ) AS learning_objectives
            FROM {schema}.exercises e
            WHERE e.activity_id = {activity_id}
            ORDER BY e.id
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )
        exercise_rows = db.execute_and_fetch(exercise_query, {
            'activity_id': self.activity_id
        })

        activity_row = activity_rows[0]
        return ActivityJSON(
            title=activity_row[0],
            description=activity_row[1],
            activity_str=activity_row[2] or '',
            search_path=activity_row[3],
            dbms=Dialect(activity_row[4]),
            domain=activity_row[5],
            exercises=[
                ExerciseJSON(
                    title=row[0],
                    request=row[1],
                    solutions=json.loads(row[2]) if row[2] else [],
                    is_hidden=row[3],
                    difficulty=row[4],
                    error=row[5],
                    learning_objectives=list(row[6] or []),
                )
                for row in exercise_rows
            ],
        )

    @staticmethod
    def load(activity: ActivityJSON, *, admin_username: str = 'lens') -> 'Activity':
        '''Load a activity and its exercises from a dumped JSON structure.'''

        admin_user = User(admin_username)
        created_activity = Activity.create(
            title=activity.title,
            description=activity.description,
            activity_str=activity.activity_str,
            domain=activity.domain,
            search_path=activity.search_path,
            dbms=Dialect(activity.dbms) or Dialect.POSTGRES,
        )
        created_activity.add_participant(admin_user)
        created_activity.set_owner_status(admin_user, True)

        for exercise in activity.exercises:
            created_exercise = Exercise.create(
                title=exercise.title,
                user=admin_user,
                activity_id=created_activity.activity_id,
                request=exercise.request,
                solutions=exercise.solutions,
                difficulty=exercise.difficulty,
                error=exercise.error,
            )
            created_exercise.set_hidden(exercise.is_hidden)

            for objective_id in exercise.learning_objectives:
                created_exercise.set_learning_objective(objective_id)

        return created_activity

    @staticmethod
    def load_json(payload: str, *, admin_username: str = 'lens') -> 'Activity':
        '''Parse a dumped activity JSON string and load it into the database.'''

        parsed_payload: dict[str, Any] = json.loads(payload)
        return Activity.load(
            ActivityJSON(
                title=parsed_payload['title'],
                description=parsed_payload['description'],
                activity_str=parsed_payload.get('activity_str', parsed_payload.get('dataset_str', '')),
                search_path=parsed_payload.get('search_path'),
                dbms=parsed_payload.get('dbms'),
                domain=parsed_payload.get('domain'),
                exercises=[
                    ExerciseJSON(
                        title=exercise['title'],
                        request=exercise['request'],
                        solutions=list(exercise.get('solutions', [])),
                        is_hidden=bool(exercise.get('is_hidden', False)),
                        difficulty=exercise.get('difficulty'),
                        error=exercise.get('error'),
                        learning_objectives=list(exercise.get('learning_objectives', [])),
                    )
                    for exercise in parsed_payload.get('exercises', [])
                ],
            ),
            admin_username=admin_username,
        )

    def dump_json(self) -> str:
        '''Dump a activity to a JSON string.'''

        return json.dumps(asdict(self.dump()), indent=2, ensure_ascii=False)

    def update(self, title: str, description: str, activity_str: str, search_path: str | None = None, dbms: Dialect | None = None, activity_start_ts: datetime | None = None, activity_end_ts: datetime | None = None) -> None:
        '''Update an existing activity'''

        query = database.sql.SQL(
        '''
            UPDATE {schema}.activities
            SET
                name = {title},
                description = {description},
                activity = {activity},
                search_path = {search_path},
                dbms = {dbms},
                activity_start_ts = {activity_start_ts},
                activity_end_ts = {activity_end_ts}
            WHERE id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            title=database.sql.Placeholder('title'),
            description=database.sql.Placeholder('description'),
            activity_id=database.sql.Placeholder('activity_id'),
            activity=database.sql.Placeholder('activity'),
            search_path=database.sql.Placeholder('search_path'),
            dbms=database.sql.Placeholder('dbms'),
            activity_start_ts=database.sql.Placeholder('activity_start_ts'),
            activity_end_ts=database.sql.Placeholder('activity_end_ts'),
        )

        db.execute(query, {
            'title': title,
            'description': description,
            'activity_id': self.activity_id,
            'activity': activity_str.strip() or None,
            'search_path': search_path,
            'dbms': dbms.value if dbms else None,
            'activity_start_ts': activity_start_ts,
            'activity_end_ts': activity_end_ts,
        })

    def delete(self) -> None:
        '''Delete a activity by its ID'''

        query = database.sql.SQL(
        '''
            DELETE FROM {schema}.activities d
            WHERE
                d.id = {activity_id}
                AND NOT EXISTS (
                    SELECT 1
                    FROM {schema}.exercises e
                    WHERE e.activity_id = d.id
                )
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        db.execute(query, {
            'activity_id': self.activity_id
        })
    # endregion

    # region Membership
    def has_owner(self, user: User) -> bool:
        '''Check if a user is an owner of a activity'''

        query = database.sql.SQL(
        '''
            SELECT
                is_owner
            FROM
                {schema}.activity_members
            WHERE
                username = {username}
                AND activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'username': user.username,
            'activity_id': self.activity_id
        })

        if len(result) == 0:
            return False
        
        return result[0][0]
    
    def has_participant(self, user: User) -> bool:
        '''Check if a user is a participant of a class'''

        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.activity_members
            WHERE
                username = {username}
                AND activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            activity_id=database.sql.Placeholder('activity_id')
        )
        result = db.execute_and_fetch(query, {
            'username': user.username,
            'activity_id': self.activity_id
        })
        return result[0][0] > 0

    def add_participant(self, user: User) -> None:
        '''Add a user as a participant of a class'''

        query = database.sql.SQL(
        '''
            INSERT INTO {schema}.activity_members (username, activity_id)
                VALUES ({username}, {activity_id})
            ON CONFLICT (username, activity_id) DO UPDATE
                SET is_active = TRUE
                WHERE activity_members.username = {username} AND activity_members.activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            activity_id=database.sql.Placeholder('activity_id')
        )

        db.execute(query, {
            'username': user.username,
            'activity_id': self.activity_id
        })

    def can_remove_participant(self, user: User) -> bool:
        '''Check if a user can leave a activity. User cannot leave if they are a teacher and the activity has at least one exercise, one student or one query assigned to it.'''

        # Allow leaving even for teachers
        return True

        if not self.has_owner(user):
            return True

        # Check if there are any exercises assigned to the class
        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.exercises
            WHERE activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        if result[0][0] > 0:
            return False
        
        # Check if there are any students in the class
        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.activity_members
            WHERE
                activity_id = {activity_id}
                AND is_owner = FALSE
                AND is_active = TRUE
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        if result[0][0] > 0:
            return False
        
        # Check if there are any queries assigned to the class
        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.query_batches qb
            JOIN {schema}.exercises e ON qb.exercise_id = e.id
            WHERE e.activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        if result[0][0] > 0:
            return False
        
        return True

    def remove_participant(self, user: User) -> bool:
        '''Leave a activity. User cannot leave if they are a teacher and the activity has at least one exercise, one student or one query assigned to it.'''

        if not self.can_remove_participant(user):
            return False

        query = database.sql.SQL(
        '''
            UPDATE {schema}.activity_members
            SET is_active = FALSE
            WHERE
                username = {username}
                AND activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            activity_id=database.sql.Placeholder('activity_id')
        )

        db.execute(query, {
            'username': user.username,
            'activity_id': self.activity_id
        })

        return True
    
    def set_owner_status(self, user: User, is_owner: bool) -> None:
        '''Set a user's owner status in a class'''

        if not self.has_participant(user):
            raise ValueError(f'User {user.username} is not a participant of activity {self.activity_id}')
        
        query = database.sql.SQL(
        '''
            UPDATE {schema}.activity_members
            SET is_owner = {is_owner}
            WHERE
                username = {username}
                AND activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            is_owner=database.sql.Placeholder('is_owner'),
            username=database.sql.Placeholder('username'),
            activity_id=database.sql.Placeholder('activity_id')
        )

        db.execute(query, {
            'username': user.username,
            'is_owner': is_owner,
            'activity_id': self.activity_id
        })

    def get_members(self) -> list[dict[str, Any]]:
        '''
            Get all members of a class, along with their teacher status

            Returns:
            A list of members with the following fields:
            - username: The username of the member
            - is_owner: Whether the member is an owner
        '''

        query = database.sql.SQL(
        '''
            SELECT
                dm.username,
                dm.is_owner
            FROM
                {schema}.activity_members dm
            WHERE
                dm.activity_id = {activity_id}
            ORDER BY
                dm.username
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        return [{
            'username': row[0],
            'is_owner': row[1]
        } for row in result]
    # endregion

    # region Exercises
    def shuffle(self, prefix: str = 'Exercise ') -> None:
        '''Shuffle activity exercises and rename them sequentially.'''

        query = database.sql.SQL(
        '''
            SELECT
                e.id,
                e.request,
                e.solutions
            FROM
                {schema}.exercises e
            WHERE
                e.activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        exercises = [
            Exercise(
                exercise_id=row[0],
                activity_id=self.activity_id,
                request=row[1],
                solutions=json.loads(row[2]),
                all_properties_loaded=True,
            )
            for row in result
        ]
        random.shuffle(exercises)

        for index, exercise in enumerate(exercises, start=1):
            exercise.update(
                title=f'{prefix}{index}',
                request=exercise.request,
                solutions=exercise.solutions,
            )

    def list_all_exercises(self) -> list[Exercise]:
        '''Get all exercises in a activity, including hidden ones.'''

        query = database.sql.SQL(
        '''
            SELECT
                e.id,
                e.title,
                e.is_hidden,
                e.request,
                e.solutions,
                e.generation_difficulty,
                e.generation_error
            FROM
                {schema}.exercises e
            WHERE
                e.activity_id = {activity_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            activity_id=database.sql.Placeholder('activity_id')
        )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        return [
            Exercise(
                exercise_id=row[0],
                activity_id=self.activity_id,
                title=row[1],
                is_hidden=row[2],
                request=row[3],
                solutions=json.loads(row[4]),
                difficulty=row[5],
                error=row[6],
                all_properties_loaded=True
            ) for row in result
        ]

    def list_exercises(self, user: User) -> list[Exercise]:
        '''Get all exercises assigned to a user in a activity. Includes hidden exercises if the user is a teacher.'''

        if self.has_owner(user):
            # User is a teacher, include hidden exercises
            query = database.sql.SQL(
            '''
                SELECT
                    e.id,
                    e.title,
                    e.is_hidden,
                    e.request,
                    e.solutions,
                    e.generation_difficulty
                FROM
                    {schema}.exercises e
                WHERE
                    e.activity_id = {activity_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                activity_id=database.sql.Placeholder('activity_id')
            )
        else:
            # User is a student, exclude hidden exercises
            query = database.sql.SQL(
            '''
                SELECT
                    e.id,
                    e.title,
                    e.is_hidden,
                    e.request,
                    e.solutions,
                    e.generation_difficulty
                FROM
                    {schema}.exercises e
                WHERE
                    e.activity_id = {activity_id}
                    AND e.is_hidden = FALSE
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                activity_id=database.sql.Placeholder('activity_id')
            )

        result = db.execute_and_fetch(query, {
            'activity_id': self.activity_id
        })

        return [
            Exercise(
                exercise_id=row[0],
                activity_id=self.activity_id,
                title=row[1],
                is_hidden=row[2],
                request=row[3],
                solutions=json.loads(row[4]),
                difficulty=row[5],
                all_properties_loaded=True
            ) for row in result
        ]
    # endregion
