import pandas as pd
import pytest

from server.db.users.database import Database
from server.sql import Column, SQLCode
from server.sql.result import QueryResultDataset, QueryResultMessage


class _BuiltinQueries:
    @staticmethod
    def show_search_path() -> str:
        return 'SHOW search_path;'

    @staticmethod
    def list_users() -> str:
        return 'SELECT * FROM users;'

    @staticmethod
    def list_schemas() -> str:
        return 'SELECT * FROM schemata;'

    @staticmethod
    def list_tables() -> str:
        return 'SELECT * FROM tables;'

    @staticmethod
    def describe_tables() -> str:
        return 'SELECT * FROM columns;'

    @staticmethod
    def list_constraints() -> str:
        return 'SELECT * FROM constraints;'


class _MetadataQueries:
    @staticmethod
    def set_search_path(search_path: str) -> str:
        return f'SET search_path TO {search_path};'

    @staticmethod
    def get_search_path() -> str:
        return 'SHOW search_path;'

    @staticmethod
    def get_columns() -> str:
        return 'SELECT 1;'

    @staticmethod
    def get_unique_columns() -> str:
        return 'SELECT 1;'


class _SolutionCheckDatabase(Database):
    def __init__(self, results_by_query, *, data_types=None):
        super().__init__(
            dbname='alice',
            port=5432,
            dbms_name='postgresql',
            admin_username='postgres',
            builtin_queries=_BuiltinQueries,
            metadata_queries=_MetadataQueries,
            data_types=data_types or {23: 'int4', 25: 'text'},
        )
        self.results_by_query = results_by_query
        self.calls = []

    def _execute_solution_check(self, query: str, *, search_path: str | None = None):
        self.calls.append((query, search_path))
        return self.results_by_query[query]

    def create_container(self):
        raise NotImplementedError

    def _get_connection(self, autocommit: bool = True):
        raise NotImplementedError


def _dataset(query: str, columns: list[Column], rows: list[list[object]]):
    return QueryResultDataset(
        result=pd.DataFrame(rows, columns=[column.name for column in columns]),
        query=SQLCode(query),
        columns=columns,
    )


@pytest.mark.parametrize(
    (
        'case_name',
        'results_by_query',
        'query_solutions',
        'expected_correct',
        'expected_execution_success',
        'expected_result_type',
        'expected_message_parts',
        'expected_calls',
        'expected_diff_rows',
    ),
    [
        (
            'basic_match',
            {
                'USER': (
                    _dataset('USER', [Column('id', 23)], [[1], [2]]),
                    True,
                ),
                'SOLUTION': (
                    _dataset('SOLUTION', [Column('id', 23)], [[1], [2]]),
                    True,
                ),
            },
            ['SOLUTION'],
            True,
            True,
            QueryResultMessage,
            ['Your query returns the same values as the solution.'],
            [('USER', None), ('SOLUTION', 'public')],
            None,
        ),
        (
            'duplicate_user_column_names',
            {
                'USER': (
                    _dataset('USER', [Column('dup', 23), Column('dup', 25)], [[1, 'a']]),
                    True,
                ),
                'SOLUTION': (
                    _dataset('SOLUTION', [Column('dup', 23), Column('dup', 25)], [[1, 'a']]),
                    True,
                ),
            },
            ['SOLUTION'],
            True,
            True,
            QueryResultMessage,
            ['Your query returns the same values as the solution.'],
            [('USER', None), ('SOLUTION', 'public')],
            None,
        ),
        (
            'types_do_not_match',
            {
                'USER': (
                    _dataset('USER', [Column('id', 25)], [[1]]),
                    True,
                ),
                'SOLUTION': (
                    _dataset('SOLUTION', [Column('id', 23)], [[1]]),
                    True,
                ),
            },
                ['SOLUTION'],
                False,
                True,
                QueryResultMessage,
                ['different data types', 'id<i>(int4</i>)', 'id<i>(text</i>)'],
                [('USER', None), ('SOLUTION', 'public')],
                None,
            ),
        (
            'column_amounts_do_not_match',
            {
                'USER': (
                    _dataset('USER', [Column('id', 23)], [[1]]),
                    True,
                ),
                'SOLUTION': (
                    _dataset('SOLUTION', [Column('id', 23), Column('name', 25)], [[1, 'a']]),
                    True,
                ),
            },
            ['SOLUTION'],
            False,
            True,
            QueryResultMessage,
            ['different columns', 'Expected:', 'Your query:'],
            [('USER', None), ('SOLUTION', 'public')],
            None,
        ),
        (
            'different_names_same_count_current_behavior',
            {
                'USER': (
                    _dataset('USER', [Column('user_name', 25)], [['alice']]),
                    True,
                ),
                'SOLUTION': (
                    _dataset('SOLUTION', [Column('solution_name', 25)], [['alice']]),
                    True,
                ),
            },
            ['SOLUTION'],
            True,
            True,
            QueryResultMessage,
            ['Your query returns the same values as the solution.'],
            [('USER', None), ('SOLUTION', 'public')],
            None,
        ),
        (
            'empty_solution_list',
            {},
            [],
            None,
            None,
            QueryResultMessage,
            ['No solution found for this exercise.'],
            [],
            None,
        ),
        (
            'multiple_solutions_uses_later_match',
            {
                'USER': (
                    _dataset('USER', [Column('id', 23)], [[2]]),
                    True,
                ),
                'WRONG_SOLUTION': (
                    _dataset('WRONG_SOLUTION', [Column('id', 23)], [[1]]),
                    True,
                ),
                'RIGHT_SOLUTION': (
                    _dataset('RIGHT_SOLUTION', [Column('id', 23)], [[2]]),
                    True,
                ),
            },
            ['WRONG_SOLUTION', 'RIGHT_SOLUTION'],
            True,
            True,
            QueryResultMessage,
            ['Your query returns the same values as the solution.'],
            [('USER', None), ('WRONG_SOLUTION', 'public'), ('RIGHT_SOLUTION', 'public')],
            None,
        ),
        (
            'different_result_rows',
            {
                'USER': (
                    _dataset('USER', [Column('id', 23)], [[1]]),
                    True,
                ),
                'SOLUTION': (
                    _dataset('SOLUTION', [Column('id', 23)], [[2]]),
                    True,
                ),
            },
            ['SOLUTION'],
            False,
            True,
            QueryResultDataset,
            [],
            [('USER', None), ('SOLUTION', 'public')],
            2,
        ),
        (
            'unsupported_user_query',
            {
                'USER': (
                    None,
                    False,
                ),
            },
            ['SOLUTION'],
            False,
            False,
            QueryResultMessage,
            ['Your query is not supported. Please ensure it is a valid SQL SELECT query.'],
            [('USER', None)],
            None,
        ),
        (
            'teacher_solution_fails',
            {
                'USER': (
                    _dataset('USER', [Column('id', 23)], [[1]]),
                    True,
                ),
                'SOLUTION': (
                    None,
                    False,
                ),
            },
            ['SOLUTION'],
            None,
            False,
            QueryResultMessage,
            ['Error executing teacher-provided solution. Have you initialized the dataset?'],
            [('USER', None), ('SOLUTION', 'public')],
            None,
        ),
    ],
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_check_query_solution_parametrized(
    case_name,
    results_by_query,
    query_solutions,
    expected_correct,
    expected_execution_success,
    expected_result_type,
    expected_message_parts,
    expected_calls,
    expected_diff_rows,
):
    database = _SolutionCheckDatabase(results_by_query)

    result = database.check_query_solution(
        query_user='USER',
        query_solutions=query_solutions,
        solution_search_path='public',
    )

    assert result.correct is expected_correct
    assert result.execution_success is expected_execution_success
    assert isinstance(result.result, expected_result_type)
    assert database.calls == expected_calls

    if expected_result_type is QueryResultMessage:
        for message_part in expected_message_parts:
            assert message_part in result.result.result_text
    else:
        assert result.result.row_count() == expected_diff_rows
        assert '__UNEXPECTED__' in result.result.result_text
        assert '__MISSING__' in result.result.result_text
