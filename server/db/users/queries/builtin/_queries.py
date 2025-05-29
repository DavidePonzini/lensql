from enum import Enum

class Queries(Enum):
    '''Queries used for builtin operations.'''
    
    SHOW_SEARCH_PATH = '''
        SHOW search_path;
    '''

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
            table_schema = current_schema()
        ORDER BY
            table_schema,
            table_name;
    '''

    LIST_ALL_TABLES = '''
        SELECT
            table_schema AS schema,
            table_name as table,
            table_type as type
        FROM
            information_schema.tables
        ORDER BY
            table_schema,
            table_name;
    '''

    LIST_CONSTRAINTS = '''
        SELECT
            tc.table_schema AS schema,
            tc.table_name AS table,
            tc.constraint_name AS constraint,
            tc.constraint_type AS type
        FROM
            information_schema.table_constraints AS tc
        WHERE
            tc.table_schema <> 'pg_catalog'
            AND tc.table_schema <> 'information_schema'
        ORDER BY
            tc.table_schema,
            tc.table_name,
            tc.constraint_name;
    '''