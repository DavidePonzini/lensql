'''This module handles message-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db, llm, gamification
from .util import responses
from server.gamification import NOT_ENOUGH_COINS_MESSAGE

from flask_babel import _

bp = Blueprint('message', __name__)

def _get_usage_badges(user: db.admin.User) -> list[gamification.Reward]:
    '''Check if the user has earned any badges related to message usage.'''
    
    badges = []

    help_usage_count = user.count_help_usage()

    for k, v in gamification.rewards.Badges.HELP_USAGE.value.items():
        if k <= help_usage_count:
            if not user.has_badge(v.reason):
                badges.append(v)

    return badges


@bp.route('/feedback', methods=['POST'])
@jwt_required()
def feedback():
    '''Log feedback for a message.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    message = db.admin.Message(data['message_id'])
    feedback = data['feedback']

    message.log_feedback(feedback=feedback, user=user)

    rewards = []
    badges = []

    rewards.append(gamification.rewards.Actions.Messages.FEEDBACK)
    feedback_count = user.count_feedbacks()

    for k  , v in gamification.rewards.Badges.FEEDBACK.value.items():
        if k <= feedback_count:
            if not user.has_badge(v.reason):
                badges.append(v)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(True, rewards=rewards, badges=badges)


@bp.route('/error/explain', methods=['POST'])
@jwt_required()
def explain_error_message():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()

    query = db.admin.Query(data['query_id'])
    msg_idx = int(data['msg_idx'])

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_EXPLAIN

    if not user.can_afford(cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)
    
    exception = query.result
    answer_str = llm.explain_error_message(user.username, query.sql_string, exception)

    answer = db.admin.Message.log(
        answer=answer_str,
        button=request.path,
        query=query,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(user)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(answer=answer_str, id=answer.message_id, rewards=rewards, badges=badges)

@bp.route('/error/locate', methods=['POST'])
@jwt_required()
def locate_error_cause():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query = db.admin.Query(data['query_id'])
    msg_idx = int(data['msg_idx'])

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_LOCATE

    if not user.can_afford(cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    exception = query.result
    answer_str = llm.locate_error_cause(user.username, query.sql_string, exception)

    answer = db.admin.Message.log(
        answer=answer_str,
        button=request.path,
        query=query,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(user)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(answer=answer_str, id=answer.message_id, rewards=rewards, badges=badges)

@bp.route('/error/example', methods=['POST'])
@jwt_required()
def provide_error_example():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query = db.admin.Query(data['query_id'])
    msg_idx = int(data['msg_idx'])

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_EXAMPLE

    if not user.can_afford(cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    exception = query.result
    answer_str = llm.provide_error_example(user.username, query.sql_string, exception)
    
    answer = db.admin.Message.log(
        answer=answer_str,
        button=request.path,
        query=query,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(user)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(answer=answer_str, id=answer.message_id, rewards=rewards, badges=badges)

@bp.route('/error/fix', methods=['POST'])
@jwt_required()
def fix_query():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query = db.admin.Query(data['query_id'])
    msg_idx = int(data['msg_idx'])

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_FIX

    if not user.can_afford(cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)
    
    exception = query.result
    answer_str = llm.fix_query(user.username, query.sql_string, exception, query.errors)

    answer = db.admin.Message.log(
        answer=answer_str,
        button=request.path,
        query=query,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(user)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(answer=answer_str, id=answer.message_id, rewards=rewards, badges=badges)

@bp.route('/success/describe', methods=['POST'])
@jwt_required()
def describe_my_query():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query = db.admin.Query(data['query_id'])
    msg_idx = int(data['msg_idx'])

    cost = gamification.rewards.Actions.Messages.HELP_SUCCESS_DESCRIBE

    if not user.can_afford(cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    answer_str = llm.describe_my_query(user.username, query.sql_string)
    answer = db.admin.Message.log(
        answer=answer_str,
        button=request.path,
        query=query,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(user)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(answer=answer_str, id=answer.message_id, rewards=rewards, badges=badges)

@bp.route('/success/explain', methods=['POST'])
@jwt_required()
def explain_my_query():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query = db.admin.Query(data['query_id'])
    msg_idx = int(data['msg_idx'])

    cost = gamification.rewards.Actions.Messages.HELP_SUCCESS_EXPLAIN

    if not user.can_afford(cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    answer_str = llm.explain_my_query(user.username, query.sql_string)
    answer = db.admin.Message.log(
        answer=answer_str,
        button=request.path,
        query=query,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(user)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(answer=answer_str, id=answer.message_id, rewards=rewards, badges=badges)

@bp.route('/success/detect-errors', methods=['POST'])
@jwt_required()
def detect_errors():
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    query = db.admin.Query(data['query_id'])
    msg_idx = int(data['msg_idx'])

    cost = gamification.rewards.Actions.Messages.HELP_SUCCESS_CHECK_ERRORS

    if not user.can_afford(cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)
    
    if not query.errors:
        return responses.response(answer=_("Congratulations, I couldn't find any errors in your query!"))

    answer_str = llm.detect_errors(user.username, query.sql_string, errors=query.errors)
    answer = db.admin.Message.log(
        answer=answer_str,
        button=request.path,
        query=query,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(user)

    user.add_rewards(rewards=rewards, badges=badges)

    return responses.response(answer=answer_str, id=answer.message_id, rewards=rewards, badges=badges)