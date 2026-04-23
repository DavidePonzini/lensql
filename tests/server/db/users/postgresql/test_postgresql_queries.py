from server.db.users.postgresql.queries import PostgresqlBuiltinQueries, PostgresqlMetadataQueries


def test_set_search_path_embeds_value_in_sql():
    sql = PostgresqlMetadataQueries.set_search_path('public, custom_schema')

    assert 'SET search_path TO public, custom_schema;' in sql


def test_list_constraints_targets_current_schema():
    sql = PostgresqlBuiltinQueries.list_constraints()

    assert 'WHERE n.nspname = current_schema()' in sql
    assert "AND c.contype <> 'n'" in sql
    assert 'ORDER BY n.nspname, t.relname, c.conname;' in sql
