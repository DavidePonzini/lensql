from ..queries import BuiltinQueries, MetadataQueries

class PostgresqlBuiltinQueries(BuiltinQueries):
    @staticmethod
    def show_search_path() -> str:
        return '''
            SHOW search_path;
        '''

    @staticmethod
    def list_users() -> str:
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
    def describe_tables() -> str:
        return '''
            SELECT
                t.relname AS table_name,
                a.attname AS column_name,
                pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
                CASE WHEN a.attnotnull THEN 'not null' ELSE '' END AS nullable,
                pg_get_expr(ad.adbin, ad.adrelid) AS default
            FROM pg_attribute a
            JOIN pg_class t
                ON a.attrelid = t.oid
            JOIN pg_namespace n
                ON t.relnamespace = n.oid
            LEFT JOIN pg_attrdef ad
                ON a.attrelid = ad.adrelid
                AND a.attnum = ad.adnum
            WHERE n.nspname = current_schema()
            AND t.relkind = 'r'
            AND a.attnum > 0
            AND NOT a.attisdropped
            ORDER BY t.relname, a.attnum;
        '''

    @staticmethod
    def list_constraints() -> str:
        return '''
            SELECT
                n.nspname AS schema_name,
                t.relname AS table_name,
                c.conname AS constraint_name,
                CASE c.contype
                    WHEN 'p' THEN 'PRIMARY KEY'
                    WHEN 'u' THEN 'UNIQUE'
                    WHEN 'f' THEN 'FOREIGN KEY'
                    WHEN 'c' THEN 'CHECK'
                    ELSE c.contype::text
                END AS constraint_type,
                CASE
                    WHEN c.contype IN ('p', 'u') THEN pk_uq.columns
                    WHEN c.contype = 'f' THEN fk.columns
                    WHEN c.contype = 'c' THEN pg_get_constraintdef(c.oid)
                    ELSE ''
                END AS constraint_info
            FROM pg_constraint c
            JOIN pg_class t
                ON t.oid = c.conrelid
            JOIN pg_namespace n
                ON n.oid = t.relnamespace

            LEFT JOIN LATERAL (
                SELECT string_agg(a.attname, ', ' ORDER BY u.ord) AS columns
                FROM unnest(c.conkey) WITH ORDINALITY AS u(attnum, ord)
                JOIN pg_attribute a
                    ON a.attrelid = c.conrelid
                AND a.attnum = u.attnum
                WHERE c.contype IN ('p', 'u')
            ) pk_uq ON TRUE

            LEFT JOIN LATERAL (
                SELECT string_agg(
                    src.attname || ' -> ' || refns.nspname || '.' || reft.relname || '.' || ref.attname,
                    ', '
                    ORDER BY u.ord
                ) AS columns
                FROM unnest(c.conkey, c.confkey) WITH ORDINALITY AS u(src_attnum, ref_attnum, ord)
                JOIN pg_attribute src
                    ON src.attrelid = c.conrelid
                AND src.attnum = u.src_attnum
                JOIN pg_class reft
                    ON reft.oid = c.confrelid
                JOIN pg_namespace refns
                    ON refns.oid = reft.relnamespace
                JOIN pg_attribute ref
                    ON ref.attrelid = c.confrelid
                AND ref.attnum = u.ref_attnum
                WHERE c.contype = 'f'
            ) fk ON TRUE

            WHERE n.nspname = current_schema()
            AND c.contype <> 'n'
            ORDER BY n.nspname, t.relname, c.conname;
        '''

    
class PostgresqlMetadataQueries(MetadataQueries):
    @staticmethod
    def set_search_path(search_path: str) -> str:
        return f'''
            SET search_path TO {search_path};
        '''

    @staticmethod
    def get_search_path() -> str:
        return '''
            SHOW search_path;
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

    @staticmethod
    def get_unique_columns() -> str:
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
