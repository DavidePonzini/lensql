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

    rewards = []
    badges = []

    # Gamification: query execution
    if db.admin.queries.is_new_query(username, query):
        rewards.append(gamification.rewards.Actions.Query.UNIQUE_RUN)
    
        unique_queries_count = db.admin.users.count_unique_queries(username)
        if unique_queries_count in gamification.rewards.Badges.QUERIES_UNIQUE:
            badges.append(gamification.rewards.Badges.QUERIES_UNIQUE[unique_queries_count])
    else:
        rewards.append(gamification.rewards.Actions.Query.RUN)

    # Gamification: query execution in own exercise
    own_exercises_with_at_least_one_own_query = db.admin.exercises.count_own_exercises_with_at_least_one_own_query(username)
    if own_exercises_with_at_least_one_own_query in gamification.rewards.Badges.CREATE_EXERCISES:
        badges.append(gamification.rewards.Badges.CREATE_EXERCISES[own_exercises_with_at_least_one_own_query])

    # Gamification: daily usage
    days_active = db.admin.users.count_days_active(username)
    if days_active in gamification.rewards.Badges.DAILY_USAGE:
        badges.append(gamification.rewards.Badges.DAILY_USAGE[days_active])

    db.admin.users.add_rewards(username, *rewards, *badges)

    def generate_results():
        yield json.dumps({
            'rewards': rewards,
            'badges': badges,
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
    attempts = db.admin.exercises.count_attempts(exercise_id, username)
    
    db.admin.exercises.log_solution_attempt(query_id=query_id, username=username, exercise_id=exercise_id, is_correct=check.correct)

    rewards = []
    badges = []

    # cost for checking the solution
    rewards.append(gamification.rewards.Actions.Exercise.check_solution_cost(attempts))

    if check.correct:
        if not already_solved:
            rewards.append(gamification.rewards.Actions.Exercise.SOLVED)

            # Gamification: check Exercise Solved badge
            solved_count = db.admin.users.count_exercises_solved(username)
            if solved_count in gamification.rewards.Badges.EXERCISE_SOLUTIONS:
                badges.append(gamification.rewards.Badges.EXERCISE_SOLUTIONS[solved_count])
        else:
            rewards.append(gamification.rewards.Actions.Exercise.REPEATED)

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response_query(
        check.result,
        is_builtin=True,
        rewards=rewards,
        badges=badges,
    )