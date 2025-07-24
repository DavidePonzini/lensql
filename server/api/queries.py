'''This module handles query-related endpoints for the API.'''

from flask import Blueprint, request
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db, gamification
from server.sql.result import QueryResult, QueryResultDataset
from .util import responses

bp = Blueprint('query', __name__)


@bp.route('/run', methods=['POST'])
@jwt_required()
def run_query():
    '''
    Run a SQL query and return the results in a streaming response.
    This endpoint is used to execute user-submitted SQL queries against the database.
    '''
    username = get_jwt_identity()
    data = request.get_json()
    query = data['query']
    exercise_id = int(data['exercise_id'])

    batch_id = db.admin.queries.log_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    if db.admin.queries.is_new_query(username, query):
        exp_change = gamification.Experience.QUERY_RUN_UNIQUE.value
        exp_change_reason = 'New query executed'
    else:
        exp_change = gamification.Experience.QUERY_RUN.value
        exp_change_reason = 'Query executed'

    db.admin.users.add_experience(username, exp_change)

    def generate_results():
        yield json.dumps({
            'exp_change': exp_change,
            'exp_change_reason': exp_change_reason,
        }) + '\n'  # Important: one JSON object per line

        for query_result in db.users.queries.execute(username=username, query_str=query):
            query_id = db.admin.queries.log(
                username=username,
                batch_id=batch_id,
                query=query_result.query.query,
                search_path=db.users.queries.metadata.get_search_path(username),
                success=query_result.success,
                result=query_result.result_text,
                query_type=query_result.query.query_type,
                query_goal=query_result.query.query_goal
            )
            query_result.id = query_id

            db.admin.queries.log_context(
                query_id=query_id,
                columns=db.users.queries.metadata.get_columns(username),
                unique_columns=db.users.queries.metadata.get_unique_columns(username)
            )

            yield json.dumps({
                'success': query_result.success,
                'builtin': False,
                'query': query_result.query.query,
                'type': query_result.data_type,
                'data': query_result.result_html,
                'id': query_id,
                'notices': query_result.notices,
            }) + '\n'  # Important: one JSON object per line

    return responses.streaming_response(generate_results())


def log_builtin_query(username: str, exercise_id: int, result: QueryResult) -> int:
    '''
    Log a built-in query result and return the query ID.
    This function is used to log the results of built-in queries executed by users.
    '''
    batch_id = db.admin.queries.log_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_id = db.admin.queries.log(
        username=username,
        batch_id=batch_id,
        query=result.query.query,
        success=result.success,
        result=result.result_text,
        query_type='BUILTIN',
        query_goal='BUILTIN'
    )

    return query_id

@bp.route('/builtin/show-search-path', methods=['POST'])
@jwt_required()
def show_search_path():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db.users.queries.builtin.show_search_path(username)
    result.id = log_builtin_query(username, exercise_id, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-schemas', methods=['POST'])
@jwt_required()
def list_schemas():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db.users.queries.builtin.list_schemas(username)
    result.id = log_builtin_query(username, exercise_id, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-tables', methods=['POST'])
@jwt_required()
def list_tables():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db.users.queries.builtin.list_tables(username)
    result.id = log_builtin_query(username, exercise_id, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-all-tables', methods=['POST'])
@jwt_required()
def list_all_tables():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db.users.queries.builtin.list_all_tables(username)
    result.id = log_builtin_query(username, exercise_id, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-constraints', methods=['POST'])
@jwt_required()
def list_constraints():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db.users.queries.builtin.list_constraints(username)
    result.id = log_builtin_query(username, exercise_id, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/check-solution', methods=['POST'])
@jwt_required()
def check_solution():
    username = get_jwt_identity()
    data = request.get_json()
    query = data['query']
    exercise_id = int(data['exercise_id'])

    solution = db.admin.exercises.get_solution(exercise_id)
    
    check = db.users.queries.builtin.solution.check(username, query_user=query, query_solution=solution)
    
    batch_id = db.admin.queries.log_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_id = db.admin.queries.log(
        username=username,
        batch_id=batch_id,
        query=query,
        success=check.execution_success,
        result=check.result.result_text,
        query_type='CHECK_SOLUTION',
        query_goal='CHECK_SOLUTION'
    )

    db.admin.queries.log_context(
        query_id=query_id,
        columns=db.users.queries.metadata.get_columns(username),
        unique_columns=db.users.queries.metadata.get_unique_columns(username)
    )

    already_solved = db.admin.exercises.is_solved(exercise_id, username)
    db.admin.exercises.log_solution_attempt(query_id=query_id, username=username, exercise_id=exercise_id, is_correct=check.correct)

    if check.correct:
        if not already_solved:
            exp_change = gamification.Experience.EXERCISE_SOLVED.value
            coins_change = gamification.Coins.EXERCISE_SOLVED.value
            change_reason = 'Exercise solved for the first time'
        else:
            exp_change = gamification.Experience.EXERCISE_SOLUTION_CHECKED.value
            coins_change = 0
            change_reason = 'Exercise solution checked'
    else:
        exp_change = 0
        coins_change = 0
        change_reason = 'Exercise solution check failed'

    db.admin.users.add_experience(username, exp_change)
    db.admin.users.add_coins(username, coins_change)

    return responses.response_query(
        check.result,
        is_builtin=True,
        exp_change=exp_change,
        coins_change=coins_change,
        change_reason=change_reason,
    )