from pathlib import Path

MIEDEMA_SQL = (Path(__file__).parents[1] / 'fixtures' / 'miedema.sql').read_text()


def test_generator_copy_keeps_tables_and_data_without_schema_or_transaction_commands():
    from server.generation.dataset import generation_dataset_sql
    import sqlglot
    from sqlglot import exp
    prepared = generation_dataset_sql(MIEDEMA_SQL)
    statements = sqlglot.parse(prepared, read='postgres')
    assert len(statements) == 12
    assert all(isinstance(statement, (exp.Create, exp.Insert)) for statement in statements)
    assert all(not table.db for statement in statements for table in statement.find_all(exp.Table))
    assert 'miedema' not in prepared.lower()

