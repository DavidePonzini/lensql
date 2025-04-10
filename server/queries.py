from enum import Enum

class Queries(Enum):
    '''Queries used for builtin operations.'''
    
    LIST_USERS = '''
        SELECT
            usename AS username
        FROM
            pg_catalog.pg_user
        ORDER BY
            usename;
    '''

    LIST_SCHEMAS = '''
        SELECT
            schema_name,
            schema_owner
        FROM
            information_schema.schemata
        ORDER BY
            schema_name;
    '''

    LIST_TABLES = '''
        SELECT
            table_schema AS schema,
            table_name as table,
            table_type as type
        FROM
            information_schema.tables
        WHERE
            table_schema <> 'pg_catalog'
            AND table_schema <> 'information_schema'
        ORDER BY
            table_schema,
            table_name;
    '''