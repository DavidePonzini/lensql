from ..queries import BuiltinQueries, MetadataQueries


class MySQLBuiltinQueries(BuiltinQueries):
    @staticmethod
    def show_search_path() -> str:
        return '''
            SELECT DATABASE() AS current_database;
        '''

    @staticmethod
    def list_users() -> str:
        return '''
            SELECT
                user AS username
            FROM
                mysql.user
            ORDER BY
                user;
        '''

    @staticmethod
    def list_schemas() -> str:
        return '''
            SELECT
                schema_name
            FROM
                information_schema.schemata
            ORDER BY
                schema_name;
        '''

    @staticmethod
    def list_tables() -> str:
        return '''
            SELECT
                table_schema AS schema_name,
                table_name AS table_name,
                table_type AS type
            FROM
                information_schema.tables
            WHERE
                table_schema = DATABASE()
            ORDER BY
                table_schema,
                table_name;
        '''

    @staticmethod
    def list_all_tables() -> str:
        return '''
            SELECT
                table_schema AS schema_name,
                table_name AS table_name,
                table_type AS type
            FROM
                information_schema.tables
            ORDER BY
                table_schema,
                table_name;
        '''

    @staticmethod
    def list_constraints() -> str:
        return '''
            SELECT
                tc.table_schema AS schema_name,
                tc.table_name,
                tc.constraint_name,
                tc.constraint_type
            FROM
                information_schema.table_constraints AS tc
            WHERE
                tc.table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY
                tc.table_schema,
                tc.table_name,
                tc.constraint_name;
        '''


class MySQLMetadataQueries(MetadataQueries):
    @staticmethod
    def set_search_path(search_path: str) -> str:
        '''Sets the search path for the user.'''
        # MySQL does not have a search_path concept like PostgreSQL.
        # Instead, we can use the "USE database" command to switch databases.
        return f'''
            USE {search_path};
        '''

    @staticmethod
    def get_search_path() -> str:
        return '''
            SELECT DATABASE() AS current_database;
        '''

    @staticmethod
    def get_columns() -> str:
        return '''
            SELECT
                cols.table_schema AS schema_name,
                cols.table_name,
                cols.column_name,
                cols.data_type AS column_type,
                cols.numeric_precision,
                cols.numeric_scale,
                (cols.is_nullable = 'YES') AS is_nullable,
                fk.referenced_table_schema AS foreign_key_schema,
                fk.referenced_table_name AS foreign_key_table,
                fk.referenced_column_name AS foreign_key_column
            FROM information_schema.columns AS cols

            LEFT JOIN information_schema.key_column_usage fk
                ON fk.table_schema = cols.table_schema
                AND fk.table_name = cols.table_name
                AND fk.column_name = cols.column_name
                AND fk.referenced_table_name IS NOT NULL

            WHERE cols.table_schema NOT IN
                ('mysql', 'information_schema', 'performance_schema', 'sys');
        '''

    @staticmethod
    def get_unique_columns() -> str:
        return '''
            SELECT
                kcu.table_schema AS schema_name,
                kcu.table_name,
                tc.constraint_type,
                CONCAT(
                    '{',
                    GROUP_CONCAT(DISTINCT kcu.column_name SEPARATOR ','),
                    '}'
                ) AS columns
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON  tc.constraint_schema = kcu.table_schema
                AND tc.table_name = kcu.table_name
                AND tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
            AND kcu.table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            GROUP BY
                kcu.table_schema,
                kcu.table_name,
                tc.constraint_name,
                tc.constraint_type;
        '''