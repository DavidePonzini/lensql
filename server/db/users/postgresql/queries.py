from ..queries import BuiltinQueries, MetadataQueries

class PostgresqlBuiltinQueries(BuiltinQueries):
    @staticmethod
    def show_search_path() -> str:
        '''Shows the search path for the database.'''
        return '''
            SHOW search_path;
        '''

    @staticmethod
    def list_users() -> str:
        '''Lists all users in the database.'''
        return '''
            SELECT
                usename AS username
            FROM
                pg_catalog.pg_user
            ORDER BY
                usename;
        '''
    
    @staticmethod
    def list_schemas() -> str:
        '''Lists all schemas in the database.'''
        return '''
            SELECT
                schema_name,
                schema_owner
            FROM
                information_schema.schemata
            ORDER BY
                schema_name;
        '''

    @staticmethod
    def list_tables() -> str:
        '''Lists tables in the current search_path.'''
        return '''
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

    @staticmethod
    def list_all_tables() -> str:
        '''Lists all tables in the database.'''
        return '''
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

    @staticmethod
    def list_constraints() -> str:
        '''Lists all constraints in the database.'''
        return '''
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

    
class PostgresqlMetadataQueries(MetadataQueries):
    @staticmethod
    def get_search_path() -> str:
        '''Returns the current search path for the user.'''
        return '''
            SHOW search_path;
        '''

    @staticmethod
    def get_columns() -> str:
        '''Lists all tables'''
        return '''
            SELECT
                kcu.table_schema AS schema_name,
                kcu.table_name,
                tc.constraint_type,
                array_agg(kcu.column_name ORDER BY kcu.ordinal_position) AS columns
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.constraint_schema = kcu.constraint_schema
            WHERE tc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
            AND kcu.table_schema NOT IN ('pg_catalog', 'information_schema')
            GROUP BY
                kcu.table_schema,
                kcu.table_name,
                kcu.constraint_name,
                tc.constraint_type;
        '''

    @staticmethod
    def get_unique_columns() -> str:
        '''Lists unique columns.'''
        return '''
            SELECT
                cols.table_schema AS schema_name,
                cols.table_name,
                cols.column_name,
                cols.data_type AS column_type,
                cols.numeric_precision,
                cols.numeric_scale,
                (cols.is_nullable = 'YES') AS is_nullable,
                fk.foreign_table_schema AS foreign_key_schema,
                fk.foreign_table_name AS foreign_key_table,
                fk.foreign_column_name AS foreign_key_column
            FROM information_schema.columns AS cols

            -- Foreign Key
            LEFT JOIN (
                SELECT
                    kcu.table_schema,
                    kcu.table_name,
                    kcu.column_name,
                    ccu.table_schema AS foreign_table_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
            ) fk ON fk.table_schema = cols.table_schema
                AND fk.table_name = cols.table_name
                AND fk.column_name = cols.column_name

            WHERE cols.table_schema NOT IN ('pg_catalog', 'information_schema')
        '''
