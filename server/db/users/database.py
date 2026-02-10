from dataclasses import dataclass

from server.sql.result.dataset import QueryResultDataset

from .connection import DatabaseConnection
from .queries import BuiltinQueries, MetadataQueries
from .solution import CheckExecutionStatus, result_dataset, result_message, CheckResult, CheckResultMessage, CheckResultDataset

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
from sqlscope.catalog import CatalogColumnInfo, CatalogUniqueConstraintInfo

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

    def get_datatype_name(self, data_type_code: int) -> str:
        '''Returns the name of the data type for the given type code, or the code itself if not found.'''
        return self.data_types.get(data_type_code, f'id={data_type_code}')

    # region SQL Execution
    def execute_sql(self, query_str: str, *, strip_comments: bool = True, builtin_name: str | None = None) -> Iterable[QueryResult]:
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

    # region Database Creation
    @abstractmethod
    def init(self, password: str) -> bool:
        '''Initializes the database.'''
        pass

    @abstractmethod
    def exists(self) -> bool:
        '''Checks if the database exists.'''
        pass
    # endregion        
    
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

        result = self.connect().execute_sql_raw(self.metadata_queries.get_search_path())

        return result[0][0]

    def get_columns(self) -> list[CatalogColumnInfo]:
        '''Lists all tables'''

        result = self.connect().execute_sql_raw(self.metadata_queries.get_columns())

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

        result = self.connect().execute_sql_raw(self.metadata_queries.get_unique_columns())

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
    def _execute_solution_check(self, query: str, *, search_path: str | None = None) -> tuple[QueryResultDataset | None, bool | None]:
        '''
            Execute the first statement of the query and return the result.

            Args:
                query (str): The SQL query to execute.
                search_path (str | None): Optional search path to set for the connection before executing the query. If None, the current search path is used.

            Returns:
                QueryResultDataset: The result of the query execution.
                bool: True if the query was executed successfully, False otherwise. None if the query was not executed (e.g. not a SELECT query).
        '''

        statements = SQLCode(query).split()

        # Only execute the first statement
        statement = next(iter(statements), None)
        if statement is None:
            return None, None

        # Only SELECT queries are supported
        if statement.query_type != 'SELECT':
            return None, None
        
        conn = None
        try:
            conn = self.connect()

            if search_path is not None:
                # Set the search path for the connection, and reset it back to the original after executing the query
                current_search_path = self.get_search_path()
                conn.execute_sql_raw(f'SET search_path TO {search_path};')

                results = conn.execute_sql(statement)
                dataset = next(iter(results), None) # iterator needs to be exhausted here, before resetting search path

                conn.execute_sql_raw(f'SET search_path TO {current_search_path};')
            else:
                results = conn.execute_sql(statement)
                dataset = next(iter(results), None)

            # If the query does not return a dataset, we don't need it
            if not isinstance(dataset, QueryResultDataset):
                return None, False

            conn.update_last_operation_ts()
            return dataset, True
        except SQLException:
            # Connection was not opened, nothing to rollback
            if conn is None:
                return None, False
            
            try:
                conn.rollback()
                conn.update_last_operation_ts()
            except Exception as e2:     # catch all to avoid handling each DB exception separately
                dav_tools.messages.error(f'Error rolling back connection for db "{self.dbname}": {e2}')
            
            return None, False

    def check_query_solution(self, query_user: str, query_solutions: list[str], solution_search_path: str) -> CheckExecutionStatus:
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

        result_user, execution_success = self._execute_solution_check(query_user)
        if result_user is None:
            message = '<i class="fa fa-exclamation-triangle text-danger me-1"></i>'
            message += _('Your query is not supported. Please ensure it is a valid SQL SELECT query.')
            return result_message(False, execution_success, message)

        results: list[CheckResult] = []
        for query_solution in query_solutions:
            result_solution, execution_success_solution = self._execute_solution_check(query_solution, search_path=solution_search_path)

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
