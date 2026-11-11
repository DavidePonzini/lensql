"""Generate and atomically save activities using the SQL exercise generator."""
import json
import random
from uuid import uuid4

import sqlexercise
from dav_tools import database
from sqlscope import Dialect

from server.db.admin.connection import db, SCHEMA
from server.db.users import get_database
from .dataset import generation_dataset_sql
from sqlglot import exp


def generate_activity(user, errors, *, title, prefix, language='en', dataset_str=None, search_path='public'):
    sandbox = get_database(user.username, Dialect.POSTGRES)
    sandbox.get_connection()
    assignment = sqlexercise.generate_assignment(
        errors=errors,
        db_host=sandbox.hostname,
        db_port=sandbox.port,
        db_user=sandbox.admin_username,
        db_password='password',
        sql_dialect=Dialect.POSTGRES,
        language=language,
        dataset_str=generation_dataset_sql(dataset_str) if dataset_str else None,
        shuffle_exercises=True,
        max_dataset_attempts=10,
        max_exercise_attempts=10,
        max_unique_attempts=10,
    )
    exercises = list(assignment.exercises)
    if len(exercises) != len(errors):
        raise ValueError('The generator did not produce all requested exercises.')
    random.shuffle(exercises)
    schema_name = search_path if dataset_str else 'p_' + uuid4().hex[:16]
    if dataset_str:
        # Apply the chosen path both while loading unqualified tables and after
        # any SET statements inside an uploaded script.
        path = exp.Literal.string(search_path).sql(dialect='postgres')
        set_path = f"SELECT set_config('search_path', {path}, false);"
        activity_sql = f'{set_path}\n{dataset_str}\n;\n{set_path}'
    else:
        activity_sql = assignment.dataset.to_sql(schema_name)
    # All saved content and membership either commit together or roll back together.
    with db.connect() as connection:
        def execute(sql, values):
            connection.execute(database.sql.SQL(sql).format(
                schema=database.sql.Identifier(SCHEMA)), values, commit=False)

        execute('''INSERT INTO {schema}.activities (name, description, activity, search_path, dbms)
            VALUES (%(title)s, '', %(activity)s, %(search_path)s, 'postgres') RETURNING id''',
            {'title': title, 'activity': activity_sql, 'search_path': schema_name})
        activity_id = connection.fetch_one()[0]
        execute('''INSERT INTO {schema}.activity_members (username, activity_id, is_owner)
            VALUES (%(username)s, %(activity_id)s, TRUE)''',
            {'username': user.username, 'activity_id': activity_id})
        for index, exercise in enumerate(exercises, 1):
            execute('''INSERT INTO {schema}.exercises
                (activity_id, title, request, solutions, created_by, generation_difficulty, generation_error, is_hidden)
                VALUES (%(activity_id)s, %(title)s, %(request)s, %(solutions)s, %(username)s,
                    %(difficulty)s, %(error)s, FALSE)''',
                {'activity_id': activity_id, 'title': f'{prefix}{index}',
                 'request': exercise.request, 'solutions': json.dumps([q.sql for q in exercise.solutions]),
                 'username': user.username, 'difficulty': exercise.difficulty.value,
                 'error': exercise.error.value})
        connection.commit()
    return activity_id
