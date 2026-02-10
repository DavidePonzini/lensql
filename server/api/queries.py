'''This module handles query-related endpoints for the API.'''

from flask import Blueprint, request
import json
from flask_jwt_extended import jwt_required, get_jwt_identity
from sql_error_categorizer import detectors, get_errors, build_catalog

from server import db, gamification
from server.sql.code import SQLCode
from server.sql.result import QueryResultMessage, QueryResult
from .util import responses
from server.db.users.solution import NAME as SOLUTION_NAME


DETECTORS = [
    detectors.SyntaxErrorDetector,
    detectors.SemanticErrorDetector,
    detectors.LogicalErrorDetector,
    detectors.ComplicationDetector,
]

bp = Blueprint('query', __name__)


@bp.route('/run', methods=['POST'])
@jwt_required()
def run_query():
    '''
    Run a SQL query and return the results in a streaming response.
    This endpoint is used to execute user-submitted SQL queries against the database.
    '''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query_str = data['query_str']
    excercise = db.admin.Exercise(data['exercise_id'])

    rewards = []
    badges = []

    # Gamification: query execution in own exercise, if this is the first query for this exercise
    # At this point, the batch has not been logged yet
    if excercise.count_query_batches(user) == 0:
        own_exercises_with_at_least_one_own_query = user.count_own_exercises_with_at_least_one_own_query()
        for k, v in gamification.rewards.Badges.CREATE_EXERCISES.value.items():
            if own_exercises_with_at_least_one_own_query >= k:
                if not user.has_badge(v.reason):
                    badges.append(v)

    # Gamification: query execution
    if db.admin.Query.is_new(query_str, user):
        rewards.append(gamification.rewards.Actions.Query.UNIQUE_RUN)
    
        unique_queries_count = user.count_unique_queries() + 1  # +1 because we haven't logged this one yet

        for k, v in gamification.rewards.Badges.QUERIES_UNIQUE.value.items():
            if unique_queries_count >= k:
                if not user.has_badge(v.reason):
                    badges.append(v)

    else:
        rewards.append(gamification.rewards.Actions.Query.RUN)

    # -------------------------- From here on, the batch is logged -------------------
    batch = db.admin.QueryBatch.log(
        user=user,
        exercise=excercise
    )

    # Gamification: daily usage
    days_active = user.count_days_active()

    for k,v in gamification.rewards.Badges.DAILY_USAGE.value.items():
        if days_active >= k:
            if not user.has_badge(v.reason):
                badges.append(v)

    user.add_rewards(rewards=rewards, badges=badges)
    exercise_solutions = excercise.solutions
    exercise_search_path = excercise.search_path
    
    def generate_results():
        yield json.dumps({
            'rewards': [reward.to_dict() for reward in rewards],
            'badges': [badge.to_dict() for badge in badges],
        }) + '\n'  # Important: one JSON object per line

        database = db.users.PostgresqlDatabase(user.username)
        import dav_tools
        for query_result in database.execute_sql(query_str=query_str):
            dav_tools.messages.debug(f'executed query: {query_str}')
            search_path = database.get_search_path()
            dav_tools.messages.debug(f'current search path: {search_path}')

            query = db.admin.Query.log(
                query_batch=batch,
                sql_string=query_result.query.query,
                search_path=search_path,
                success=query_result.success,
                result=query_result.result_text,
                query_type=query_result.query.query_type,
                query_goal=query_result.query.query_goal
            )
            query_result.query_id = query.query_id

            dav_tools.messages.debug(f'context columns')
            context_columns = database.get_columns()
            dav_tools.messages.debug(f'context columns: {context_columns}')
            context_unique_columns = database.get_unique_columns()
            dav_tools.messages.debug(f'context unique columns: {context_unique_columns}')

            # Log context and errors for SELECT queries
            if query_result.query.query_type == 'SELECT':
                query.log_context(
                    columns=context_columns,
                    unique_columns=context_unique_columns
                )

                catalog = build_catalog(
                    columns_info=context_columns,
                    unique_constraints_info=context_unique_columns
                )

                errors = get_errors(
                    query_str=query_result.query.query,
                    solutions=exercise_solutions,
                    catalog=catalog,
                    search_path=search_path,
                    solution_search_path=exercise_search_path,
                    detectors=DETECTORS,
                    debug=True
                )
                print(flush=True)   # Ensure all debug output is flushed

                query.log_errors(errors)

            yield json.dumps({
                'success': query_result.success,
                'builtin': False,
                'query': query_result.query.query,
                'type': query_result.data_type,
                'data': query_result.result_html,
                'id': query.query_id,
                'notices': query_result.notices,
            }) + '\n'  # Important: one JSON object per line

    return responses.streaming_response(generate_results())


def log_builtin_query(user: db.admin.User, exercise: db.admin.Exercise, result: QueryResult) -> int:
    '''
    Log a built-in query result and return the query ID.
    This function is used to log the results of built-in queries executed by users.
    '''

    batch = db.admin.QueryBatch.log(
        user=user,
        exercise=exercise
    )

    query = db.admin.Query.log(
        query_batch=batch,
        sql_string=result.query.query,
        search_path='BUILTIN',
        success=result.success,
        result=result.result_text,
        query_type='BUILTIN',
        query_goal='BUILTIN'
    )

    return query.query_id

@bp.route('/builtin/show-search-path', methods=['POST'])
@jwt_required()
def show_search_path():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))
    
    database = db.users.PostgresqlDatabase(user.username)
    result = database.builtin_show_search_path()
    result = next(iter(result))
    result.query_id = log_builtin_query(user, exercise, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-schemas', methods=['POST'])
@jwt_required()
def list_schemas():
    user = db.admin.User(get_jwt_identity())
    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))
    
    database = db.users.PostgresqlDatabase(user.username)
    result = database.builtin_list_schemas()
    result = next(iter(result))
    result.query_id = log_builtin_query(user, exercise, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-tables', methods=['POST'])
@jwt_required()
def list_tables():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))
    
    database = db.users.PostgresqlDatabase(user.username)
    result = database.builtin_list_tables()
    result = next(iter(result))
    result.query_id = log_builtin_query(user, exercise, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-all-tables', methods=['POST'])
@jwt_required()
def list_all_tables():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))
    
    database = db.users.PostgresqlDatabase(user.username)
    result = database.builtin_list_all_tables()
    result = next(iter(result))
    result.query_id = log_builtin_query(user, exercise, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/builtin/list-constraints', methods=['POST'])
@jwt_required()
def list_constraints():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))
    
    database = db.users.PostgresqlDatabase(user.username)
    result = database.builtin_list_constraints()
    result = next(iter(result))
    result.query_id = log_builtin_query(user, exercise, result)

    return responses.response_query(result, is_builtin=True)

@bp.route('/check-solution', methods=['POST'])
@jwt_required()
def check_solution():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query_str = data['query']
    exercise = db.admin.Exercise(int(data['exercise_id']))

    coins = user.get_coins()
    attempts = exercise.count_attempts(user)
    cost = gamification.rewards.Actions.Exercise.check_solution_cost(attempts)  # value is negative

    if coins + cost.coins < 0:
        return responses.response_query(
            QueryResultMessage(gamification.NOT_ENOUGH_COINS_MESSAGE, query=SQLCode(SOLUTION_NAME, builtin=True)),
            is_builtin=True,
            attempts=attempts,
        )

    database = db.users.PostgresqlDatabase(user.username)
    check = database.check_query_solution(query_user=query_str, query_solutions=exercise.solutions, solution_search_path=exercise.search_path)

    batch = db.admin.QueryBatch.log(
        user=user,
        exercise=exercise
    )

    query = db.admin.Query.log(
        query_batch=batch,
        sql_string=query_str,
        search_path='BUILTIN',
        success=check.execution_success == True,
        result=check.result.result_text,
        query_type='CHECK_SOLUTION',
        query_goal='CHECK_SOLUTION'
    )

    query.log_context(
        columns=database.get_columns(),
        unique_columns=database.get_unique_columns()
    )

    already_solved = exercise.has_been_solved_by_user(user)
    
    query.log_solution_attempt(check.correct == True)

    rewards = []
    badges = []

    # cost for checking the solution
    rewards.append(gamification.rewards.Actions.Exercise.check_solution_cost(attempts))

    if check.correct:
        if not already_solved:
            rewards.append(gamification.rewards.Actions.Exercise.SOLVED)

            # Gamification: check Exercise Solved badge
            solved_count = user.count_exercises_solved()

            for k,v in gamification.rewards.Badges.EXERCISE_SOLUTIONS.value.items():
                if solved_count >= k:
                    if not user.has_badge(v.reason):
                        badges.append(v)
        else:
            rewards.append(gamification.rewards.Actions.Exercise.REPEATED)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response_query(
        check.result,
        is_builtin=True,
        rewards=rewards,
        badges=badges,
        attempts=attempts + 1,
    )
