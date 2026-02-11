from dav_tools import database
import json

from .connection import db, SCHEMA
from .users import User

class Exercise:
    '''Class for managing exercises'''

    def __init__(self, exercise_id: int, *,
                 dataset_id: str | None = None,
                 is_hidden: bool = False,
                 title: str | None = None,
                 request: str | None = None,
                 solutions: list[str] | None = None,
                 search_path: str | None = None,
                 difficulty: int | None = None,
                 learning_objectives: list[str] | None = None,
                 all_properties_loaded: bool = False
                ) -> None:
        self.exercise_id = exercise_id

        # Lazy properties
        self._properties_loaded = all_properties_loaded
        self._dataset_id = dataset_id
        self._is_hidden = is_hidden
        self._title = title
        self._request = request
        self._solutions = solutions
        self._search_path = search_path
        self._difficulty = difficulty
        self._learning_objectives = learning_objectives
    
    # region Properties
    @property
    def dataset_id(self) -> str:
        '''Get the dataset ID this exercise belongs to'''

        if not self._properties_loaded:
            self._load_properties()

        assert self._dataset_id is not None, "Dataset ID should be loaded by _load_properties"

        return self._dataset_id

    @property
    def is_hidden(self) -> bool:
        '''Check if the exercise is hidden from students'''

        if not self._properties_loaded:
            self._load_properties()

        assert self._is_hidden is not None, "is_hidden should be loaded by _load_properties"

        return self._is_hidden
    
    @property
    def title(self) -> str:
        '''Get the title of the exercise'''

        if not self._properties_loaded:
            self._load_properties()

        assert self._title is not None, "Title should be loaded by _load_properties"

        return self._title

    @property
    def request(self) -> str:
        '''Get the request (description) of the exercise'''

        if not self._properties_loaded:
            self._load_properties()

        assert self._request is not None, "Request should be loaded by _load_properties"

        return self._request
    
    @property
    def solutions(self) -> list[str]:
        '''Get the solutions of the exercise'''

        if not self._properties_loaded:
            self._load_properties()

        assert self._solutions is not None, "Solutions should be loaded by _load_properties"

        return self._solutions
    
    @property
    def search_path(self) -> str:
        '''Get the search path of the exercise'''

        if not self._properties_loaded:
            self._load_properties()

        assert self._search_path is not None, "Search path should be loaded by _load_properties"

        return self._search_path

    @property
    def difficulty(self) -> int | None:
        '''Get the difficulty level of the exercise'''

        if not self._properties_loaded:
            self._load_properties()

        return self._difficulty

    @property
    def learning_objectives(self) -> list[str]:
        '''Get the learning objectives of the exercise'''

        if self._learning_objectives is None:
            query = database.sql.SQL(
            '''
                SELECT
                    hlo.objective_id
                FROM
                    {schema}.has_learning_objective hlo
                WHERE
                    hlo.exercise_id = {exercise_id}
                ORDER BY
                    hlo.objective_id
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                exercise_id=database.sql.Placeholder('exercise_id')
            )

            result = db.execute_and_fetch(query, {
                'exercise_id': self.exercise_id
            })

            self._learning_objectives = [ row[0] for row in result ]

        return self._learning_objectives

    def count_attempts(self, user: User) -> int:
        '''Get the number of solution attempts for an exercise by a user'''

        query = database.sql.SQL('''
            SELECT COUNT(*)
            FROM
                {schema}.exercise_solutions es
                JOIN {schema}.queries q ON es.id = q.id
                JOIN {schema}.query_batches qb ON q.batch_id = qb.id
            WHERE exercise_id = {exercise_id}
            AND username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id'),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'exercise_id': self.exercise_id,
            'username': user.username
        })

        return result[0][0] if result else 0

    def count_query_batches(self, user: User) -> int:
        '''Get the number of query batches for an exercise by a user'''

        query = database.sql.SQL('''
            SELECT COUNT(*)
            FROM {schema}.query_batches
            WHERE exercise_id = {exercise_id}
            AND username = {username}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id'),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'exercise_id': self.exercise_id,
            'username': user.username
        })

        return result[0][0] if result else 0

    def has_been_solved_by_user(self, user: User) -> bool:
        '''Check if an exercise has been solved by a user'''

        query = database.sql.SQL(
        '''
            SELECT EXISTS (
                SELECT 1
                FROM
                    {schema}.exercise_solutions es
                    JOIN {schema}.queries q ON es.id = q.id
                    JOIN {schema}.query_batches qb ON q.batch_id = qb.id
                WHERE
                    qb.exercise_id = {exercise_id}
                    AND qb.username = {username}
                    AND is_correct = TRUE
            )
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id'),
            username=database.sql.Placeholder('username')
        )

        result = db.execute_and_fetch(query, {
            'exercise_id': self.exercise_id,
            'username': user.username
        })

        return result[0][0] if result else False
    # endregion

    # region CRUD Operations
    def _load_properties(self) -> None:
        # NOTE: since we usually access multiple properties at once, we load them all together
        '''Load properties from the database. Since multiple properties are often accessed together, they are all loaded at once.'''

        query = database.sql.SQL(
        '''
            SELECT
                e.title,
                e.dataset_id,
                e.is_hidden,
                e.request,
                e.solutions,
                e.search_path,
                e.generation_difficulty
            FROM
                {schema}.exercises e
            WHERE
                e.id = {exercise_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id')
        )

        result = db.execute_and_fetch(query, {
            'exercise_id': self.exercise_id
        })

        if len(result) == 0:
            raise ValueError(f'Exercise with ID {self.exercise_id} does not exist.')

        row = result[0]
        self._title = row[0]
        self._dataset_id = row[1]
        self._is_hidden = row[2]
        self._request = row[3]
        self._solutions = json.loads(row[4])
        self._search_path = row[5]
        self._difficulty = row[6]

    @staticmethod
    def create(title: str, *,
               user: User,
               dataset_id: str,
               request: str,
               solutions: list[str] = [],
               search_path: str = 'public',
               difficulty: int | None = None,
               error: int | None = None
              ) -> 'Exercise':
        '''Create a new exercise. New exercises are visible by default.'''

        result = db.insert(SCHEMA, 'exercises', {
            'title': title,
            'dataset_id': dataset_id,
            'is_hidden': False,
            'request': request,
            'solutions': json.dumps(solutions),
            'search_path': search_path,
            'created_by': user.username,
            'generation_difficulty': difficulty,
            'generation_error': error
        }, ['id'])

        assert result is not None and len(result) == 1, "Insert should return the new exercise ID"

        exercise_id = int(result[0][0])

        return Exercise(exercise_id=exercise_id,
                        dataset_id=dataset_id,
                        is_hidden=False,
                        title=title,
                        request=request,
                        solutions=solutions,
                        search_path=search_path,
                        difficulty=difficulty)

    def update(self, *, title: str, request: str, solutions: list[str] = [], search_path: str = 'public') -> None:
        '''Update an existing exercise'''

        query = database.sql.SQL('''
            UPDATE {schema}.exercises
            SET title = {title},
                request = {request},
                solutions = {solutions},
                search_path = {search_path}
            WHERE id = {exercise_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            title=database.sql.Placeholder('title'),
            request=database.sql.Placeholder('request'),
            solutions=database.sql.Placeholder('solutions'),
            search_path=database.sql.Placeholder('search_path'),
            exercise_id=database.sql.Placeholder('exercise_id'),
        )
        db.execute(query, {
            'title': title,
            'request': request,
            'solutions': json.dumps(solutions),
            'search_path': search_path,
            'exercise_id': self.exercise_id
        })

    def delete(self) -> bool:
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
                'exercise_id': self.exercise_id
            })

            return True
        except Exception:
            return False
    # endregion

    # region Learning Objectives
    def set_learning_objective(self, objective_id: str, is_set: bool = True) -> None:
        '''Set a learning objective for an exercise'''

        if not is_set:
            return self._unset_learning_objective(objective_id)

        query = database.sql.SQL('''
            INSERT INTO {schema}.has_learning_objective (exercise_id, objective_id)
            VALUES ({exercise_id}, {objective_id})
            ON CONFLICT (exercise_id, objective_id) DO NOTHING
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id'),
            objective_id=database.sql.Placeholder('objective_id')
        )

        db.execute(query, {
            'exercise_id': self.exercise_id,
            'objective_id': objective_id
        })

    def _unset_learning_objective(self, objective_id: str) -> None:
        '''Unset a learning objective for an exercise'''

        query = database.sql.SQL('''
            DELETE FROM {schema}.has_learning_objective
            WHERE exercise_id = {exercise_id}
            AND objective_id = {objective_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id'),
            objective_id=database.sql.Placeholder('objective_id')
        )

        db.execute(query, {
            'exercise_id': self.exercise_id,
            'objective_id': objective_id
        })

    def list_all_learning_objectives_status(self) -> list[tuple[str, bool]]:
        '''List all learning objectives status for an exercise'''

        query = database.sql.SQL('''
            SELECT
                lo.id,
                (hlo.objective_id IS NOT NULL) AS is_set
            FROM
                {schema}.learning_objectives lo
                LEFT JOIN {schema}.has_learning_objective hlo ON lo.id = hlo.objective_id AND hlo.exercise_id = {exercise_id}
            ORDER BY
                lo.id
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            exercise_id=database.sql.Placeholder('exercise_id')
        )

        result = db.execute_and_fetch(query, {
            'exercise_id': self.exercise_id
        })

        return [(row[0], row[1]) for row in result]
    # endregion

    # region Visibility
    def set_hidden(self, is_hidden: bool) -> None:
        '''Hide or unhide an exercise from students'''

        query = database.sql.SQL('''
            UPDATE {schema}.exercises
            SET is_hidden = {is_hidden}
            WHERE id = {exercise_id}
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            is_hidden=database.sql.Placeholder('is_hidden'),
            exercise_id=database.sql.Placeholder('exercise_id')
        )

        db.execute(query, {
            'exercise_id': self.exercise_id,
            'is_hidden': is_hidden
        })
    # endregion