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
    def describe_tables() -> str:
        return '''
            SELECT
                cols.table_name AS table_name,
                cols.column_name AS column_name,
                cols.column_type AS data_type,
                CASE
                    WHEN cols.is_nullable = 'NO' THEN 'not null'
                    ELSE ''
                END AS nullable,
                cols.column_default AS `default`
            FROM
                information_schema.columns AS cols
            JOIN
                information_schema.tables AS tables
                ON tables.table_schema = cols.table_schema
                AND tables.table_name = cols.table_name
            WHERE
                cols.table_schema = DATABASE()
                AND tables.table_type = 'BASE TABLE'
            ORDER BY
                cols.table_name,
                cols.ordinal_position;
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
                tc.constraint_type,
                CASE
                    WHEN tc.constraint_type IN ('PRIMARY KEY', 'UNIQUE') THEN pk_uq.columns
                    WHEN tc.constraint_type = 'FOREIGN KEY' THEN fk.columns
                    WHEN tc.constraint_type = 'CHECK' THEN cc.check_clause
                    ELSE ''
                END AS constraint_info
            FROM
                information_schema.table_constraints AS tc
            LEFT JOIN (
                SELECT
                    kcu.constraint_schema,
                    kcu.table_name,
                    kcu.constraint_name,
                    GROUP_CONCAT(
                        kcu.column_name
                        ORDER BY kcu.ordinal_position
                        SEPARATOR ', '
                    ) AS columns
                FROM
                    information_schema.key_column_usage AS kcu
                WHERE
                    kcu.constraint_schema = DATABASE()
                    AND kcu.referenced_table_name IS NULL
                GROUP BY
                    kcu.constraint_schema,
                    kcu.table_name,
                    kcu.constraint_name
            ) AS pk_uq
                ON pk_uq.constraint_schema = tc.constraint_schema
                AND pk_uq.table_name = tc.table_name
                AND pk_uq.constraint_name = tc.constraint_name
            LEFT JOIN (
                SELECT
                    kcu.constraint_schema,
                    kcu.table_name,
                    kcu.constraint_name,
                    GROUP_CONCAT(
                        CONCAT(
                            kcu.column_name,
                            ' -> ',
                            kcu.referenced_table_schema,
                            '.',
                            kcu.referenced_table_name,
                            '.',
                            kcu.referenced_column_name
                        )
                        ORDER BY kcu.ordinal_position
                        SEPARATOR ', '
                    ) AS columns
                FROM
                    information_schema.key_column_usage AS kcu
                WHERE
                    kcu.constraint_schema = DATABASE()
                    AND kcu.referenced_table_name IS NOT NULL
                GROUP BY
                    kcu.constraint_schema,
                    kcu.table_name,
                    kcu.constraint_name
            ) AS fk
                ON fk.constraint_schema = tc.constraint_schema
                AND fk.table_name = tc.table_name
                AND fk.constraint_name = tc.constraint_name
            LEFT JOIN
                information_schema.check_constraints AS cc
                ON cc.constraint_schema = tc.constraint_schema
                AND cc.constraint_name = tc.constraint_name
            WHERE
                tc.table_schema = DATABASE()
            ORDER BY
                schema_name,
                table_name,
                constraint_name;
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

            LEFT JOIN (
                SELECT
                    kcu.table_schema,
                    kcu.table_name,
                    kcu.column_name,
                    kcu.referenced_table_schema,
                    kcu.referenced_table_name,
                    kcu.referenced_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_schema = kcu.constraint_schema
                    AND tc.table_name = kcu.table_name
                    AND tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
            ) AS fk
                ON fk.table_schema = cols.table_schema
                AND fk.table_name = cols.table_name
                AND fk.column_name = cols.column_name

            WHERE cols.table_schema NOT IN
                ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY
                cols.table_schema,
                cols.table_name,
                cols.ordinal_position;
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
                    GROUP_CONCAT(kcu.column_name ORDER BY kcu.ordinal_position SEPARATOR ','),
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
