"""Generate and atomically save activities using the SQL exercise generator."""
import json
import random
from threading import Lock
from uuid import uuid4

import sqlexercise
from dav_tools import database
from sqlscope import Dialect

from server.db.admin.connection import db, SCHEMA
from server.db.users import get_database
from .dataset import generation_dataset_sql
from sqlglot import exp


def _target_query(lock=False):
    query = database.sql.SQL("""
        SELECT COALESCE(a.activity, ''), a.search_path, COALESCE(a.dbms, 'postgres')
        FROM {schema}.activities a
        JOIN {schema}.activity_members m ON m.activity_id = a.id
        WHERE a.id = %(activity_id)s AND m.username = %(username)s
            AND m.is_active AND m.is_owner
    """).format(schema=database.sql.Identifier(SCHEMA))
    return query + database.sql.SQL(' FOR UPDATE OF a, m') if lock else query


def get_generation_target(user, activity_id):
    rows = db.execute_and_fetch(_target_query(), {'activity_id': activity_id, 'username': user.username})
    return rows[0] if rows else None


def generate_activity(user, errors, *, title, prefix, language='en', dataset_str=None, search_path='public', on_progress=None, student_username=None, target_activity_id=None, target=None):
    on_progress = on_progress or (lambda event: None)
    completed = failed = 0
    progress_lock = Lock()

    def exercise_finished(success):
        nonlocal completed, failed
        with progress_lock:
            completed += int(success)
            failed += int(not success)
            on_progress(dict(stage='exercises', completed=completed, failed=failed, total=len(errors)))

    if target_activity_id is not None:
        dataset_str, search_path, _ = target
    prepared_dataset = generation_dataset_sql(dataset_str) if dataset_str else None
    if target_activity_id is not None and not prepared_dataset:
        raise ValueError('The activity has no dataset tables for generation.')

    on_progress(dict(stage='preparing', total=len(errors)))
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
        dataset_str=prepared_dataset,
        shuffle_exercises=True,
        on_dataset_generation_progress=lambda attempt, maximum: on_progress(
            dict(stage='dataset', attempt=attempt, maximum=maximum)),
        on_dataset_generation_success=lambda: on_progress(
            dict(stage='exercises', completed=0, failed=0, total=len(errors))),
        on_exercise_generation_success=lambda error, difficulty: exercise_finished(True),
        on_exercise_generation_failure=lambda error, difficulty: exercise_finished(False),
        max_dataset_attempts=10,
        max_exercise_attempts=10,
        max_unique_attempts=10,
    )
    exercises = list(assignment.exercises)
    if not exercises:
        raise ValueError('The generator did not produce any exercises.')
    on_progress(dict(stage='saving', completed=len(exercises), failed=len(errors) - len(exercises), total=len(errors)))
    random.shuffle(exercises)
    with db.connect() as connection:
        def execute(sql, values):
            connection.execute(database.sql.SQL(sql).format(
                schema=database.sql.Identifier(SCHEMA)), values, commit=False)

        existing_titles = set()
        if target_activity_id is not None:
            activity_id = target_activity_id
            values = {'activity_id': activity_id, 'username': user.username}
            connection.execute(_target_query(lock=True), values, commit=False)
            if connection.fetch_one() != target:
                raise ValueError('The destination activity changed during generation.')
            execute('SELECT title FROM {schema}.exercises WHERE activity_id = %(activity_id)s', values)
            existing_titles = {row[0] for row in connection.fetch_all()}
        else:
            schema_name = search_path if dataset_str else 'p_' + uuid4().hex[:16]
            if dataset_str:
                # Apply the path before and after any SET statements in the script.
                path = exp.Literal.string(search_path).sql(dialect='postgres')
                set_path = f"SELECT set_config('search_path', {path}, false);"
                activity_sql = f'{set_path}\n{dataset_str}\n;\n{set_path}'
            else:
                activity_sql = assignment.dataset.to_sql(schema_name)
            execute('''INSERT INTO {schema}.activities (name, description, activity, search_path, dbms)
                VALUES (%(title)s, '', %(activity)s, %(search_path)s, 'postgres') RETURNING id''',
                {'title': title, 'activity': activity_sql, 'search_path': schema_name})
            activity_id = connection.fetch_one()[0]
            execute('''INSERT INTO {schema}.activity_members (username, activity_id, is_owner)
                VALUES (%(username)s, %(activity_id)s, TRUE)''',
                {'username': user.username, 'activity_id': activity_id})
            if student_username:
                execute('''INSERT INTO {schema}.activity_members (username, activity_id, is_owner)
                    VALUES (%(username)s, %(activity_id)s, FALSE)''',
                    {'username': student_username, 'activity_id': activity_id})

        index = 1
        for exercise in exercises:
            while f'{prefix}{index}' in existing_titles:
                index += 1
            exercise_title = f'{prefix}{index}'
            index += 1
            execute('''INSERT INTO {schema}.exercises
                (activity_id, title, request, solutions, created_by, generation_difficulty, generation_error, is_hidden)
                VALUES (%(activity_id)s, %(title)s, %(request)s, %(solutions)s, %(username)s,
                    %(difficulty)s, %(error)s, FALSE)''',
                {'activity_id': activity_id, 'title': exercise_title,
                 'request': exercise.request, 'solutions': json.dumps([q.sql for q in exercise.solutions]),
                 'username': user.username, 'difficulty': exercise.difficulty.value,
                 'error': exercise.error.value})
        connection.commit()
    return activity_id
