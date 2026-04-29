import json
import random
from dataclasses import asdict, dataclass
from typing import Any
from dav_tools import database
from .connection import db, SCHEMA

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
    created_by: str | None


@dataclass(frozen=True)
class DatasetJSON:
    dataset_id: str
    title: str
    description: str
    dataset_str: str
    search_path: str | None
    dbms: str | None
    domain: str | None
    exercises: list[ExerciseJSON]

class Dataset:
    '''Dataset-related database operations'''

    def __init__(
        self,
        dataset_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        dataset_str: str | None = None,
        search_path: str | None = None,
        dbms: str | None = None
    ) -> None:
        self.dataset_id = dataset_id

        # Lazy properties
        self._name = name
        self._description = description
        self._dataset_str = dataset_str
        self._search_path = search_path
        self._dbms = dbms

    # region Properties
    def _load_properties(self) -> None:
        '''Load all properties of the dataset from the database'''

        query = database.sql.SQL(
        '''
            SELECT
                name,
                description,
                dataset,
                search_path
            FROM {schema}.datasets
            WHERE id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        if len(result) == 0:
            raise ValueError(f'Dataset with ID {self.dataset_id} does not exist.')

        self._name = result[0][0]
        self._description = result[0][1]
        self._dataset_str = result[0][2] or ''
        self._search_path = result[0][3]

    @property
    def name(self) -> str:
        '''Get the name of the dataset'''

        if self._name is None:
            self._load_properties()

            if self._name is None:
                raise ValueError(f'Failed to load name for dataset with ID {self.dataset_id}')
        return self._name
    
    @property
    def description(self) -> str:
        '''Get the description of the dataset'''

        if self._description is None:
            self._load_properties()

            if self._description is None:
                raise ValueError(f'Failed to load description for dataset with ID {self.dataset_id}')
        
        return self._description
    
    @property
    def dataset_str(self) -> str:
        '''Get the dataset string'''

        if self._dataset_str is None:
            self._load_properties()

            if self._dataset_str is None:
                raise ValueError(f'Failed to load dataset string for dataset with ID {self.dataset_id}')
        
        return self._dataset_str
    
    @property
    def dbms(self) -> str:
        '''Get the DBMS of the dataset'''

        if self._dbms is None:
            query = database.sql.SQL(
            '''
                SELECT dbms
                FROM {schema}.datasets
                WHERE id = {dataset_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                dataset_id=database.sql.Placeholder('dataset_id')
            )

            result = db.execute_and_fetch(query, {
                'dataset_id': self.dataset_id
            })

            if len(result) == 0:
                raise ValueError(f'Dataset with ID {self.dataset_id} does not exist.')

            self._dbms = result[0][0] or ''
        
        return self._dbms

    @property
    def domain(self) -> str | None:
        '''Get the domain of the dataset'''

        query = database.sql.SQL(
        '''
            SELECT domain
            FROM {schema}.datasets
            WHERE id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        if len(result) == 0:
            raise ValueError(f'Dataset with ID {self.dataset_id} does not exist.')

        return result[0][0]
    
    @property
    def is_special(self) -> bool:
        '''Check if the dataset is special (ID contains a special character)'''
        return not self.dataset_id.isalnum()
    
    @property
    def search_path(self) -> str:
        '''Get the search path for the dataset'''

        if self._search_path is None:
            self._load_properties()

            if self._search_path is None:
                raise ValueError(f'Failed to load search path for dataset with ID {self.dataset_id}')
        return self._search_path
    # endregion

    # region CRUD
    def exists(self) -> bool:
        '''Check if a dataset exists by its ID'''

        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.datasets
            WHERE id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        return result[0][0] > 0

    @staticmethod
    def create(
        title: str,
        description: str,
        dataset_str: str,
        *,
        domain: str | None = None,
        dataset_id: str | None = None,
        search_path: str | None = None,
        dbms: str,
    ) -> 'Dataset':
        '''Create a new dataset, optionally with a specified ID'''

        if dataset_id is not None:
            result = db.insert(SCHEMA, 'datasets', {
                'id': dataset_id,
                'name': title,
                'description': description,
                'dataset': dataset_str.strip() or None,
                'domain': domain,
                'search_path': search_path,
                'dbms': dbms,
            }, ['id'])
        else:
            result = db.insert(SCHEMA, 'datasets', {
                'name': title,
                'description': description,
                'dataset': dataset_str.strip() or None,
                'domain': domain,
                'search_path': search_path,
                'dbms': dbms,
            }, ['id'])

        assert result is not None and len(result) > 0, 'Failed to create dataset'

        dataset_id = result[0][0]

        return Dataset(dataset_id, name=title, description=description, dataset_str=dataset_str, search_path=search_path, dbms=dbms)

    def dump(self) -> DatasetJSON:
        '''Dump a dataset and its exercises to a JSON-serializable structure.'''

        dataset_query = database.sql.SQL(
        '''
            SELECT
                id,
                name,
                description,
                dataset,
                search_path,
                dbms,
                domain
            FROM {schema}.datasets
            WHERE id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )
        dataset_rows = db.execute_and_fetch(dataset_query, {
            'dataset_id': self.dataset_id
        })
        if not dataset_rows:
            raise ValueError(f'Dataset with ID {self.dataset_id} does not exist.')

        exercise_query = database.sql.SQL(
        '''
            SELECT
                e.title,
                e.request,
                e.solutions,
                e.is_hidden,
                e.generation_difficulty,
                e.generation_error,
                e.created_by,
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
            WHERE e.dataset_id = {dataset_id}
            ORDER BY e.id
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )
        exercise_rows = db.execute_and_fetch(exercise_query, {
            'dataset_id': self.dataset_id
        })

        dataset_row = dataset_rows[0]
        return DatasetJSON(
            dataset_id=dataset_row[0],
            title=dataset_row[1],
            description=dataset_row[2],
            dataset_str=dataset_row[3] or '',
            search_path=dataset_row[4],
            dbms=dataset_row[5],
            domain=dataset_row[6],
            exercises=[
                ExerciseJSON(
                    title=row[0],
                    request=row[1],
                    solutions=json.loads(row[2]) if row[2] else [],
                    is_hidden=row[3],
                    difficulty=row[4],
                    error=row[5],
                    created_by=row[6],
                    learning_objectives=list(row[7] or []),
                )
                for row in exercise_rows
            ],
        )

    @staticmethod
    def load(dataset: DatasetJSON, *, admin_username: str = 'lens') -> 'Dataset':
        '''Load a dataset and its exercises from a dumped JSON structure.'''

        admin_user = User(admin_username)
        created_dataset = Dataset.create(
            title=dataset.title,
            description=dataset.description,
            dataset_str=dataset.dataset_str,
            domain=dataset.domain,
            search_path=dataset.search_path,
            dbms=dataset.dbms or 'postgresql',
        )
        created_dataset.add_participant(admin_user)
        created_dataset.set_owner_status(admin_user, True)

        for exercise in dataset.exercises:
            created_exercise = Exercise.create(
                title=exercise.title,
                user=User(exercise.created_by or admin_username),
                dataset_id=created_dataset.dataset_id,
                request=exercise.request,
                solutions=exercise.solutions,
                difficulty=exercise.difficulty,
                error=exercise.error,
            )
            created_exercise.set_hidden(exercise.is_hidden)

            for objective_id in exercise.learning_objectives:
                created_exercise.set_learning_objective(objective_id)

        return created_dataset

    @staticmethod
    def load_json(payload: str, *, admin_username: str = 'lens') -> 'Dataset':
        '''Parse a dumped dataset JSON string and load it into the database.'''

        parsed_payload: dict[str, Any] = json.loads(payload)
        return Dataset.load(
            DatasetJSON(
                dataset_id=parsed_payload['dataset_id'],
                title=parsed_payload['title'],
                description=parsed_payload['description'],
                dataset_str=parsed_payload.get('dataset_str', ''),
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
                        created_by=exercise.get('created_by'),
                    )
                    for exercise in parsed_payload.get('exercises', [])
                ],
            ),
            admin_username=admin_username,
        )

    def dump_json(self) -> str:
        '''Dump a dataset to a JSON string.'''

        return json.dumps(asdict(self.dump()), indent=2, ensure_ascii=False)

    def update(self, title: str, description: str, dataset_str: str, search_path: str | None = None, dbms: str | None = None) -> None:
        '''Update an existing dataset'''

        query = database.sql.SQL(
        '''
            UPDATE {schema}.datasets
            SET
                name = {title},
                description = {description},
                dataset = {dataset},
                search_path = {search_path},
                dbms = {dbms}
            WHERE id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            title=database.sql.Placeholder('title'),
            description=database.sql.Placeholder('description'),
            dataset_id=database.sql.Placeholder('dataset_id'),
            dataset=database.sql.Placeholder('dataset'),
            search_path=database.sql.Placeholder('search_path'),
            dbms=database.sql.Placeholder('dbms'),
        )

        db.execute(query, {
            'title': title,
            'description': description,
            'dataset_id': self.dataset_id,
            'dataset': dataset_str.strip() or None,
            'search_path': search_path,
            'dbms': dbms,
        })

    def delete(self) -> None:
        '''Delete a dataset by its ID'''

        query = database.sql.SQL(
        '''
            DELETE FROM {schema}.datasets d
            WHERE
                d.id = {dataset_id}
                AND NOT EXISTS (
                    SELECT 1
                    FROM {schema}.exercises e
                    WHERE e.dataset_id = d.id
                )
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        db.execute(query, {
            'dataset_id': self.dataset_id
        })
    # endregion

    # region Membership
    def has_owner(self, user: User) -> bool:
        '''Check if a user is an owner of a dataset'''

        query = database.sql.SQL(
        '''
            SELECT
                is_owner
            FROM
                {schema}.dataset_members
            WHERE
                username = {username}
                AND dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'username': user.username,
            'dataset_id': self.dataset_id
        })

        if len(result) == 0:
            return False
        
        return result[0][0]
    
    def has_participant(self, user: User) -> bool:
        '''Check if a user is a participant of a class'''

        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.dataset_members
            WHERE
                username = {username}
                AND dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            dataset_id=database.sql.Placeholder('dataset_id')
        )
        result = db.execute_and_fetch(query, {
            'username': user.username,
            'dataset_id': self.dataset_id
        })
        return result[0][0] > 0

    def add_participant(self, user: User) -> None:
        '''Add a user as a participant of a class'''

        query = database.sql.SQL(
        '''
            INSERT INTO {schema}.dataset_members (username, dataset_id)
                VALUES ({username}, {dataset_id})
            ON CONFLICT (username, dataset_id) DO UPDATE
                SET is_active = TRUE
                WHERE dataset_members.username = {username} AND dataset_members.dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        db.execute(query, {
            'username': user.username,
            'dataset_id': self.dataset_id
        })

    def can_remove_participant(self, user: User) -> bool:
        '''Check if a user can leave a dataset. User cannot leave if they are a teacher and the dataset has at least one exercise, one student or one query assigned to it.'''

        if not self.has_owner(user):
            return True

        # Check if there are any exercises assigned to the class
        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.exercises
            WHERE dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        if result[0][0] > 0:
            return False
        
        # Check if there are any students in the class
        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.dataset_members
            WHERE
                dataset_id = {dataset_id}
                AND is_owner = FALSE
                AND is_active = TRUE
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        if result[0][0] > 0:
            return False
        
        # Check if there are any queries assigned to the class
        query = database.sql.SQL(
        '''
            SELECT COUNT(*)
            FROM {schema}.query_batches qb
            JOIN {schema}.exercises e ON qb.exercise_id = e.id
            WHERE e.dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        if result[0][0] > 0:
            return False
        
        return True

    def remove_participant(self, user: User) -> bool:
        '''Leave a dataset. User cannot leave if they are a teacher and the dataset has at least one exercise, one student or one query assigned to it.'''

        if not self.can_remove_participant(user):
            return False

        query = database.sql.SQL(
        '''
            UPDATE {schema}.dataset_members
            SET is_active = FALSE
            WHERE
                username = {username}
                AND dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        db.execute(query, {
            'username': user.username,
            'dataset_id': self.dataset_id
        })

        return True
    
    def set_owner_status(self, user: User, is_owner: bool) -> None:
        '''Set a user's owner status in a class'''

        if not self.has_participant(user):
            raise ValueError(f'User {user.username} is not a participant of dataset {self.dataset_id}')
        
        query = database.sql.SQL(
        '''
            UPDATE {schema}.dataset_members
            SET is_owner = {is_owner}
            WHERE
                username = {username}
                AND dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            is_owner=database.sql.Placeholder('is_owner'),
            username=database.sql.Placeholder('username'),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        db.execute(query, {
            'username': user.username,
            'is_owner': is_owner,
            'dataset_id': self.dataset_id
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
                {schema}.dataset_members dm
            WHERE
                dm.dataset_id = {dataset_id}
            ORDER BY
                dm.username
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        return [{
            'username': row[0],
            'is_owner': row[1]
        } for row in result]
    # endregion

    # region Exercises
    def shuffle(self, prefix: str = 'Exercise ') -> None:
        '''Shuffle dataset exercises and rename them sequentially.'''

        query = database.sql.SQL(
        '''
            SELECT
                e.id,
                e.request,
                e.solutions
            FROM
                {schema}.exercises e
            WHERE
                e.dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        exercises = [
            Exercise(
                exercise_id=row[0],
                dataset_id=self.dataset_id,
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

    def list_exercises(self, user: User) -> list[Exercise]:
        '''Get all exercises assigned to a user in a dataset. Includes hidden exercises if the user is a teacher.'''

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
                    e.dataset_id = {dataset_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                dataset_id=database.sql.Placeholder('dataset_id')
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
                    e.dataset_id = {dataset_id}
                    AND e.is_hidden = FALSE
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                dataset_id=database.sql.Placeholder('dataset_id')
            )

        result = db.execute_and_fetch(query, {
            'dataset_id': self.dataset_id
        })

        return [
            Exercise(
                exercise_id=row[0],
                dataset_id=self.dataset_id,
                title=row[1],
                is_hidden=row[2],
                request=row[3],
                solutions=json.loads(row[4]),
                difficulty=row[5],
                all_properties_loaded=True
            ) for row in result
        ]
    # endregion
