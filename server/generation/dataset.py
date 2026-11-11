"""Prepare user SQL for the generator's temporary validation schemas."""
import sqlglot
from sqlglot import exp


def generation_dataset_sql(sql):
    statements = sqlglot.parse(sql, read='postgres')
    statements = [statement for statement in statements if isinstance(statement, (exp.Create, exp.Insert))
                  and (not isinstance(statement, exp.Create) or statement.kind.upper() == 'TABLE')]
    tables = [table for statement in statements for table in statement.find_all(exp.Table)]
    schemas = {table.db for table in tables if table.db}
    # The generator validates each exercise in a temporary schema. Strip the input
    # schema from table references so it never writes into the user's own schema.
    if len(schemas) > 1 or any(table.catalog for table in tables):
        raise ValueError('Use a dataset containing tables from a single schema.')
    if not schemas:
        return sql
    for table in tables:
        table.set('db', None)
    return '\n'.join(statement.sql(dialect='postgres') + ';' for statement in statements)
