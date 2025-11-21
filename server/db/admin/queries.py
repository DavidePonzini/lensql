from dav_tools import database
from .connection import db, SCHEMA
from sql_error_categorizer import DetectedError
from sql_error_categorizer.catalog import CatalogColumnInfo, CatalogUniqueConstraintInfo

from .users import User
from .exercises import Exercise

class QueryBatch:
    '''Class for logging and retrieving query batches.'''

    def __init__(self, batch_id: int, *,
                 exercise: Exercise | None = None,
                 user: User | None = None
                ) -> None:
        self.batch_id = batch_id

        # lazy-loaded properties
        self._exercise = exercise
        self._user = user

    @property
    def exercise(self) -> Exercise:
        '''Get the exercise associated with this query batch.'''

        if self._exercise is None:
            query = database.sql.SQL('''
                SELECT exercise_id
                FROM {schema}.query_batches
                WHERE id = {batch_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                batch_id=database.sql.Placeholder('batch_id')
            )
            result = db.execute_and_fetch(query, {
                'batch_id': self.batch_id
            })

            self._exercise = Exercise(result[0][0])

        return self._exercise
    
    @property
    def user(self) -> User:
        '''Get the user associated with this query batch.'''

        if self._user is None:
            query = database.sql.SQL('''
                SELECT username
                FROM {schema}.query_batches
                WHERE id = {batch_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                batch_id=database.sql.Placeholder('batch_id')
            )
            result = db.execute_and_fetch(query, {
                'batch_id': self.batch_id
            })
            username = result[0][0]
            self._user = User(username)

        return self._user

    @staticmethod
    def log(user: User, exercise_id: int) -> 'QueryBatch':
        '''Log a new query batch for a user and exercise ID.'''

        result = db.insert(SCHEMA, 'query_batches', {
            'username': user.username,
            'exercise_id': exercise_id,
        }, ['id'])

        assert result is not None and len(result) == 1 and len(result[0]) == 1, 'Failed to log query batch.'
        
        batch_id = result[0][0]
        return QueryBatch(batch_id, user=user, exercise_id=exercise_id)

class Query:
    '''Class for logging and retrieving user queries.'''

    def __init__(self, query_id: int, *,
                 sql_string: str | None = None,
                 search_path: str | None = None,
                 query_batch: QueryBatch | None = None,
                 result: str | None = None
                ) -> None:
        self.query_id = query_id

        # lazy-loaded properties
        self._sql_string = sql_string
        self._search_path = search_path
        self._query_batch = query_batch
        self._result = result

    # region Properties
    @property
    def user(self) -> User:
        '''Get the username associated with this query.'''

        return self.query_batch.user

    @property
    def exercise(self) -> Exercise:
        '''Get the exercise associated with this query.'''

        return self.query_batch.exercise

    @property
    def query_batch(self) -> QueryBatch:
        '''Get the query batch associated with this query.'''

        if self._query_batch is None:
            query = database.sql.SQL('''
                SELECT batch_id
                FROM {schema}.queries
                WHERE id = {query_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                query_id=database.sql.Placeholder('query_id')
            )
            result = db.execute_and_fetch(query, {
                'query_id': self.query_id
            })
            batch_id = result[0][0]
            self._query_batch = QueryBatch(batch_id)

        return self._query_batch

    @property
    def sql_string(self) -> str:
        '''Get the SQL string associated with this query.'''

        if self._sql_string is None:
            query = database.sql.SQL('''
                SELECT query
                FROM {schema}.queries
                WHERE id = {query_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                query_id=database.sql.Placeholder('query_id')
            )
            result = db.execute_and_fetch(query, {
                'query_id': self.query_id
            })
            self._sql_string = result[0][0]

        return self._sql_string

    @property
    def search_path(self) -> str:
        '''Get the search path associated with this query.'''

        if self._search_path is None:
            query = database.sql.SQL('''
                SELECT search_path
                FROM {schema}.queries
                WHERE id = {query_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                query_id=database.sql.Placeholder('query_id')
            )
            result = db.execute_and_fetch(query, {
                'query_id': self.query_id
            })
            self._search_path = result[0][0]

        return self._search_path

    @property
    def result(self) -> str:
        '''Get the result string associated with this query.'''

        if self._result is None:
            query = database.sql.SQL('''
                SELECT result
                FROM {schema}.queries
                WHERE id = {query_id}
            ''').format(
                schema=database.sql.Identifier(SCHEMA),
                query_id=database.sql.Placeholder('query_id')
            )
            result = db.execute_and_fetch(query, {
                'query_id': self.query_id
            })
            self._result = result[0][0]

        return self._result
    # endregion

    # region Logging
    @staticmethod
    def log(*,
            query_batch: QueryBatch,
            sql_string: str,
            search_path: str,
            success: bool,
            result: str,
            query_type: str,
            query_goal: str) -> 'Query':
        '''Log a new query with its result and success status.'''

        res = db.insert(SCHEMA, 'queries', {
            'batch_id': query_batch.batch_id,
            'query': sql_string,
            'search_path': search_path,
            'success': success,
            'result': result,
            'query_type': query_type,
            'query_goal': query_goal,
        }, ['id'])

        assert res is not None and len(res) == 1 and len(res[0]) == 1, 'Failed to log query.'

        query_id = int(res[0][0])
        query = Query(query_id, sql_string=sql_string, search_path=search_path, query_batch=query_batch)

        # Log in unique queries table
        if query_type != 'BUILTIN':
            query.log_uniqueness()

        return query
    
    def log_uniqueness(self) -> None:
        '''Log the query as a unique query for the user.'''

        statement = database.sql.SQL(
            '''
            INSERT INTO {schema}.user_unique_queries (username, query_hash)
            VALUES ({username}, MD5({query}))
            ON CONFLICT (username, query_hash) DO NOTHING
            '''
        ).format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            query=database.sql.Placeholder('query')
        )
        db.execute(statement, {
            'username': self.user.username,
            'query': self.sql_string
        })

    def log_errors(self, errors: list[DetectedError]) -> None:
        '''Log errors for a given query'''

        for error in errors:
            db.insert(SCHEMA, 'has_error', {
                'query_id': self.query_id,
                'error_id': error.error.value,
                'details': [str(v) for v in error.data]
            })

    def is_new(self) -> bool:
        '''Check if a query is new for the user.'''

        statement = database.sql.SQL('''
            SELECT COUNT(*)
            FROM {schema}.user_unique_queries
            WHERE username = {username}
            AND query_hash = MD5({query})
        ''').format(
            schema=database.sql.Identifier(SCHEMA),
            username=database.sql.Placeholder('username'),
            query=database.sql.Placeholder('query')
        )

        result = db.execute_and_fetch(statement, {
            'username': self.user.username,
            'query': self.sql_string
        })

        return result[0][0] == 0

    def log_context(self, columns: list[CatalogColumnInfo], unique_columns: list[CatalogUniqueConstraintInfo]) -> None:
        '''Log context for a query.'''

        for column in columns:
            db.insert(SCHEMA, 'query_context_columns', {
                'query_id': self.query_id,
                'schema_name': column.schema_name,
                'table_name': column.table_name,
                'column_name': column.column_name,
                'column_type': column.column_type,
                'numeric_precision': column.numeric_precision,
                'numeric_scale': column.numeric_scale,
                'is_nullable': column.is_nullable,
                'foreign_key_schema': column.foreign_key_schema,
                'foreign_key_table': column.foreign_key_table,
                'foreign_key_column': column.foreign_key_column,
            })

        for column in unique_columns:
            db.insert(SCHEMA, 'query_context_columns_unique', {
                'query_id': self.query_id,
                'schema_name': column.schema_name,
                'table_name': column.table_name,
                'constraint_type': column.constraint_type,
                'columns': column.columns,
            })

    def log_solution_attempt(self, is_correct: bool) -> None:
        '''Log a solution attempt for an exercise'''

        db.insert(SCHEMA, 'exercise_solutions', {
            'id': self.query_id,
            'is_correct': is_correct,
        })
