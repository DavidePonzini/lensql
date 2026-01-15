from dataclasses import dataclass

from .connection import DatabaseConnection
from .queries import BuiltinQueries, MetadataQueries
from .solution import CheckSolutionResult, result_dataset, result_message

from server.sql import SQLCode, QueryResult, SQLException, QueryResultError, Column

from abc import ABC, abstractmethod
import threading
import time
import datetime
import os
import dav_tools
from typing import Iterable
import pandas as pd
from flask_babel import _
from sql_error_categorizer.catalog import CatalogColumnInfo, CatalogUniqueConstraintInfo

MAX_CONNECTION_AGE = datetime.timedelta(hours=float(os.getenv('MAX_CONNECTION_HOURS', '4')))
CLEANUP_INTERVAL_SECONDS = int(os.getenv('CLEANUP_INTERVAL_SECONDS', '60'))

class Database(ABC):
    connections: dict[str, DatabaseConnection] = {}
    '''Pool of active connections. Keyed by dbname (which always matches the username).'''
    conn_lock: threading.Lock = threading.Lock()
    '''Lock for accessing the connections pool.'''
    
    admin_username: str = ''
    '''Username of the admin user for this database type.'''

    builtin_queries: type[BuiltinQueries]
    '''Class containing raw SQL queries for built-in operations.'''
    metadata_queries: type[MetadataQueries]
    '''Class containing raw SQL queries for metadata operations.'''

    data_types: dict[int, str] = {}
    '''Mapping of data type codes to their names.'''

    def __init__(self, dbname: str):
        self.dbname = dbname

    # region SQL Execution
    def execute_sql(self, query_str: str, strip_comments: bool = True, *, builtin_name: str | None = None) -> Iterable[QueryResult]:
        '''
        Executes the given SQL queries and returns the results.
        The queries will be separated into individual statements.

        Parameters:
            query_str (str): The SQL query string to execute. The query string can contain multiple SQL statements separated by semicolons.
            strip_comments (bool): Whether to strip comments from the SQL code before execution. Default is True.
        Returns:
            Iterable[QueryResult]: An iterable of QueryResult objects.
        '''

        for statement in SQLCode(query_str).split():
            # NOTE: do not `strip_comments` from the SQL code for very large queries
            #   as it takes the server too much time to parse the SQL code,
            #   causing a timeout error in the client.
            if strip_comments:
                statement = statement.strip_comments()

            conn = None
            try:
                conn = self.connect()

                # run each query
                for result in conn.execute_sql(statement):
                    # if a builtin query name is provided, replace its SQL with its shorter name
                    if builtin_name is not None:
                        result.query = SQLCode(builtin_name, builtin=True)
                    
                    yield result

                conn.update_last_operation_ts()
            except SQLException as e:
                if conn is None:
                    return # cannot rollback if no connection
                
                try:
                    conn.rollback()
                    conn.update_last_operation_ts()
                except Exception as e2:     # catch all to avoid handling each DB exception separately
                    dav_tools.messages.error(f'Error rolling back connection for db "{self.dbname}": {e2}')
                
                yield QueryResultError(
                    exception=e,
                    query=statement if builtin_name is None else SQLCode(builtin_name, builtin=True),
                    notices=conn.notices)
    # endregion

    @abstractmethod
    def init(self, password: str) -> bool:
        '''Initializes the database.'''
        pass

    @abstractmethod
    def exists(self) -> bool:
        '''Checks if the database exists.'''
        pass

    def get_datatype_name(self, data_type_code: int) -> str:
        '''Returns the name of the data type for the given type code, or the code itself if not found.'''
        return self.data_types.get(data_type_code, f'id={data_type_code}')
        
    
    # region Connections
    @abstractmethod
    def _get_connection(self, username: str, autocommit: bool = True) -> DatabaseConnection:
        '''Gets a connection for the specified user.'''
        pass

    def connect(self, autocommit: bool = True) -> DatabaseConnection:
        '''Connects to the database as the specified user.'''
        
        if self.dbname in self.connections:
            conn = self.connections[self.dbname]
            conn.clear_notices()
            return conn
        
        with self.conn_lock:
            conn = self._get_connection(self.dbname, autocommit=autocommit)
            self.connections[self.dbname] = conn
            return conn

    def connect_as_admin(self, autocommit: bool = True) -> DatabaseConnection:
        '''
            Connects to the database as the admin user.
            This connection is not added to the connection pool.
        '''
        return self._get_connection(self.admin_username, autocommit=autocommit)
    # endregion

    # region Cleanup
    @staticmethod
    def _connection_cleanup_thread() -> None:
        '''
        Thread that cleans up idle connections.
        '''
        while True:
            # Sleep first to avoid immediate cleanup on startup
            time.sleep(CLEANUP_INTERVAL_SECONDS)

            with Database.conn_lock:
                to_remove = []  # don't remove while iterating

                for username, conn in Database.connections.items():
                    if conn.time_since_last_operation.total_seconds() > 300:  # 5 minutes idle
                        conn.close()
                        to_remove.append(username)

                for username in to_remove:
                    try:
                        del Database.connections[username]
                        dav_tools.messages.info(f"Closed expired connection for user: {username}")
                    except Exception as e:
                        dav_tools.messages.error(f"Error closing connection for user {username}: {e}")

    @staticmethod
    def start_cleanup_thread() -> None:
        '''
            Starts a thread that will periodically check for expired connections
            and close them if they are older than MAX_CONNECTION_AGE.
        '''
        cleanup_thread = threading.Thread(target=Database._connection_cleanup_thread, daemon=True)
        cleanup_thread.start()
    # endregion

    # region Builtin Queries
    def builtin_show_search_path(self) -> Iterable[QueryResult]:
        '''Shows the search path for the database.'''

        yield from self.execute_sql(self.builtin_queries.show_search_path(), builtin_name='SHOW_SEARCH_PATH')

    def builtin_list_users(self) -> Iterable[QueryResult]:
        '''Lists all users in the database.'''

        yield from self.execute_sql(self.builtin_queries.list_users(), builtin_name='LIST_USERS')

    def builtin_list_schemas(self) -> Iterable[QueryResult]:
        '''Lists all schemas in the database.'''
        
        yield from self.execute_sql(self.builtin_queries.list_schemas(), builtin_name='LIST_SCHEMAS')

    def builtin_list_tables(self) -> Iterable[QueryResult]:
        '''Lists tables in the current search_path.'''

        yield from self.execute_sql(self.builtin_queries.list_tables(), builtin_name='LIST_TABLES')

    def builtin_list_all_tables(self) -> Iterable[QueryResult]:
        '''Lists all tables in the database.'''

        yield from self.execute_sql(self.builtin_queries.list_all_tables(), builtin_name='LIST_ALL_TABLES')

    def builtin_list_constraints(self) -> Iterable[QueryResult]:
        '''Lists all constraints in the database.'''

        yield from self.execute_sql(self.builtin_queries.list_constraints(), builtin_name='LIST_CONSTRAINTS')
    # endregion

    # region Metadata Queries
    def get_search_path(self) -> str:
        '''Returns the current search path for the user.'''

        with self.connect() as conn:
            result = conn.execute_sql_unsafe(self.metadata_queries.get_search_path())

        return result[0][0]

    def get_columns(self) -> list[CatalogColumnInfo]:
        '''Lists all tables'''

        with self.connect() as conn:
            result = conn.execute_sql_unsafe(self.metadata_queries.get_columns())

        return [
            CatalogColumnInfo(
                schema_name=row[0],
                table_name=row[1],
                column_name=row[2],
                column_type=row[3],
                numeric_precision=row[4],
                numeric_scale=row[5],
                is_nullable=row[6],
                foreign_key_schema=row[7],
                foreign_key_table=row[8],
                foreign_key_column=row[9],
            )
            for row in result
        ]

    def get_unique_columns(self) -> list[CatalogUniqueConstraintInfo]:
        '''Lists unique columns.'''

        with self.connect() as conn:
            result = conn.execute_sql_unsafe(self.metadata_queries.get_unique_columns())

        return [
            CatalogUniqueConstraintInfo(
                schema_name=row[0],
                table_name=row[1],
                constraint_type=row[2],
                columns=row[3]
            )
            for row in result
        ]
    # endregion

    # region Solution Checking
    def check_query_solution(self, query_user: str, query_solutions: list[str]) -> CheckSolutionResult:
        '''
        Checks the user's solution against the exercise solution.
        If multiple queries are present, only the first one is checked.
        If the exercise has no solution, a message is returned.
        Args:
            query_user (str): The SQL query submitted by the user.
            query_solutions (list[str]): The list of SQL solutions for the exercise.

        Returns:
            tuple: A tuple containing a boolean indicating if the solution is correct and a QueryResult object.
            If the solution is correct, the QueryResult object contains a success message.
            If the solution is incorrect, the QueryResult object contains the comparison of results.
            If the exercise has no solution, a message indicating that is returned.
        '''
        if len(query_solutions) == 0:
            message = _('No solution found for this exercise.')
            return result_message(None, None, message)

        result_user, execution_success = _execute(username, query_user)
        if result_user is None:
            message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
            message += _('Your query is not supported. Please ensure it is a valid SQL SELECT query.')
            return result_message(False, execution_success, message)

        @dataclass
        class CheckResult(ABC):
            correct: bool | None
            execution_success: bool | None

            @abstractmethod
            def to_result(self) -> CheckSolutionResult:
                pass

        @dataclass
        class CheckResultMessage(CheckResult):
            message: str

            def to_result(self) -> CheckSolutionResult:
                return result_message(self.correct, self.execution_success, self.message)

        @dataclass
        class CheckResultDataset(CheckResult):
            result: pd.DataFrame
            columns: list[Column]

            def to_result(self) -> CheckSolutionResult:
                return result_dataset(self.correct, self.execution_success, self.result, self.columns)

        results: list[CheckResult] = []
        for query_solution in query_solutions:
            result_solution, execution_success_solution = _execute(username, query_solution)
            if result_solution is None:
                message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
                message += _('Teacher-provided solution is not supported.')

                results.append(CheckResultMessage(correct=None, execution_success=execution_success_solution, message=message))
                continue

            # ensure both results have the same columns
            if not result_user.compare_column_names(result_solution):
                message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
                message += _('Your query has different columns from the solution. Cannot compare results.') + '<br/>'
                message += _('Expected:') + f' <code>{"</code>, <code>".join([col.name for col in result_solution.columns])}</code><br/>'
                message += _('Your query:') + f' <code>{"</code>, <code>".join([col.name for col in result_user.columns])}</code><br/>'

                results.append(CheckResultMessage(correct=False, execution_success=execution_success, message=message))
                continue

            # check for wrong data types
            wrong_types = result_user.compare_column_types(result_solution)

            if wrong_types:
                message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
                message += _('Your query has different data types from the solution. Cannot compare results.') + '<br/>'
                message += _('Expected:') + f' <code>{"</code>, <code>".join([f"{col.name}<i>({self.get_datatype_name(col.data_type)}</i>)" for col in result_solution.columns])}</code><br/>'
                message += _('Your query:') + f' <code>{"</code>, <code>".join([f"{col.name}<i>({self.get_datatype_name(col.data_type)}</i>)" for col in result_user.columns])}</code><br/>'

                results.append(CheckResultMessage(correct=False, execution_success=execution_success, message=message))
                continue

            has_same_result, comparison = result_user.compare_results(result_solution)

            if has_same_result:
                message = '<i class="fa fa-check text-success me-1"></i>'
                message += _('Solution is correct.') + '<br/>'
                result = CheckResultMessage(correct=True, execution_success=execution_success, message=message)
                return result.to_result()
            else:
                results.append(CheckResultDataset(correct=False, execution_success=execution_success, result=comparison, columns=result_user.columns))

        # If none of the solutions were correct, return the first incorrect result
        return results[0].to_result()
