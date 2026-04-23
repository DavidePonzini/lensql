import pandas as pd

from server.db.users.database import Database
from server.sql.code import SQLCode
from server.sql.result import Column, QueryResultDataset, QueryResultMessage


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


class _TestDatabase(Database):
    def __init__(self):
        super().__init__(
            dbname='alice',
            port=5432,
            dbms_name='postgresql',
            admin_username='postgres',
            builtin_queries=_BuiltinQueries,
            metadata_queries=_MetadataQueries,
            data_types={},
        )
        self.results = []

    def execute_sql(self, query_str: str, *, strip_comments: bool = True, builtin_name: str | None = None):
        yield from self.results

    def create_container(self):
        raise NotImplementedError

    def _get_connection(self, autocommit: bool = True):
        raise NotImplementedError


def _dataset(rows):
    return QueryResultDataset(
        result=pd.DataFrame(rows, columns=['name']),
        query=SQLCode('SELECT * FROM tables'),
        columns=[Column('name', 'text')],
    )


def test_builtin_command_returns_fallback_message_for_empty_dataset():
    database = _TestDatabase()
    database.results = [_dataset([])]

    result = list(database.builtin_command(
        query='SELECT * FROM tables;',
        builtin_name='LIST_TABLES',
        fallback_message='No tables found.',
    ))

    assert len(result) == 1
    assert isinstance(result[0], QueryResultMessage)
    assert result[0].query.query == 'LIST_TABLES'
    assert result[0].result_text == 'No tables found.'


def test_builtin_command_preserves_non_empty_dataset_results():
    database = _TestDatabase()
    dataset = _dataset([['users']])
    database.results = [dataset]

    result = list(database.builtin_command(
        query='SELECT * FROM tables;',
        builtin_name='LIST_TABLES',
        fallback_message='No tables found.',
    ))

    assert result == [dataset]


def test_get_datatype_name_returns_name_or_fallback_id():
    database = _TestDatabase()
    database.data_types = {23: 'int4'}

    assert database.get_datatype_name(23) == 'int4'
    assert database.get_datatype_name(9999) == 'id=9999'
