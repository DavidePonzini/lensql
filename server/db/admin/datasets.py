from typing import Any
from dav_tools import database
from .connection import db, SCHEMA

from .users import User
from .exercises import Exercise

class Dataset:
    '''Dataset-related database operations'''

    def __init__(self, dataset_id: int, *,
                 name: str | None = None,
                 dataset_str: str | None = None
                ) -> None:
        self.dataset_id = dataset_id

        # Lazy properties
        self._name = name
        self._dataset_str = dataset_str

    # region Properties
    @property
    def name(self) -> str:
        '''Get the name of the dataset'''

        if self._name is None:
            query = database.sql.SQL(
            '''
                SELECT name
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
        
        return self._name
    
    @property
    def dataset_str(self) -> str:
        '''Get the dataset string'''

        if self._dataset_str is None:
            query = database.sql.SQL(
            '''
                SELECT dataset
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

            self._dataset_str = result[0][0] or ''
        
        return self._dataset_str
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
    def create(title: str, dataset: str) -> 'Dataset':
        '''Create a new dataset'''

        result = db.insert(SCHEMA, 'datasets', {
            'name': title,
            'dataset': dataset.strip() or None
        }, ['id'])

        assert result is not None and len(result) > 0, 'Failed to create dataset'

        dataset_id = int(result[0][0])

        return Dataset(dataset_id, name=title, dataset_str=dataset)

    def update(self, title: str, dataset: str) -> None:
        '''Update an existing dataset'''

        query = database.sql.SQL(
        '''
            UPDATE {schema}.datasets
            SET
                name = {title},
                dataset = {dataset}
            WHERE id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            title=database.sql.Placeholder('title'),
            dataset_id=database.sql.Placeholder('dataset_id'),
            dataset=database.sql.Placeholder('dataset')
        )

        db.execute(query, {
            'title': title,
            'dataset_id': self.dataset_id,
            'dataset': dataset.strip() or None
        })

    def delete(self) -> None:
        '''Delete a dataset by its ID'''

        query = database.sql.SQL(
        '''
            DELETE FROM {schema}.datasets
            WHERE id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        db.execute(query, {
            'dataset_id': self.dataset_id
        })
    # endregion

    # region Membership
    def has_teacher(self, user: User) -> bool:
        '''Check if a user is a teacher of a class'''

        query = database.sql.SQL(
        '''
            SELECT
                is_teacher
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
            INSERT INTO {schema}.dataset_members (username, dataset_id, is_teacher)
                VALUES ({username}, {dataset_id}, FALSE)
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

        if not self.has_teacher(user):
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
                AND is_teacher = FALSE
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
    
    def set_teacher_status(self, user: User, is_teacher: bool) -> None:
        '''Set a user's teacher status in a class'''

        if not self.has_participant(user):
            raise ValueError(f'User {user.username} is not a participant of class {self.dataset_id}')
        
        query = database.sql.SQL(
        '''
            UPDATE {schema}.dataset_members
            SET is_teacher = {is_teacher}
            WHERE
                username = {username}
                AND dataset_id = {dataset_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            is_teacher=database.sql.Placeholder('is_teacher'),
            username=database.sql.Placeholder('username'),
            dataset_id=database.sql.Placeholder('dataset_id')
        )

        db.execute(query, {
            'username': user.username,
            'is_teacher': is_teacher,
            'dataset_id': self.dataset_id
        })

    def get_members(self) -> list[dict[str, Any]]:
        '''
            Get all members of a class, along with their teacher status

            Returns:
            A list of members with the following fields:
            - username: The username of the member
            - is_teacher: Whether the member is a teacher
        '''

        query = database.sql.SQL(
        '''
            SELECT
                dm.username,
                dm.is_teacher
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
            'is_teacher': row[1]
        } for row in result]
    # endregion

    # region Exercises
    def list_exercises(self, user: User) -> list[Exercise]:
        '''Get all exercises assigned to a user in a dataset. Includes hidden exercises if the user is a teacher.'''

        if self.has_teacher(user):
            # User is a teacher, include hidden exercises
            query = database.sql.SQL(
            '''
                SELECT
                    e.id
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
                    e.id
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

        return [Exercise(row[0], dataset_id=self.dataset_id) for row in result]
    # endregion