'''This module handles message-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db, llm, gamification
from .util import responses

bp = Blueprint('message', __name__)


NOT_ENOUGH_COINS_MESSAGE = "You don't have enough coins to use this feature. You can earn coins by providing feedback on Lens's answers."

def _check_coins(username: str, cost: gamification.Reward) -> bool:
    '''Check if the user has enough coins to perform an action.'''
    coins = db.admin.users.get_coins(username)
    return coins >= abs(cost)

def _get_usage_badges(username: str) -> list[gamification.Reward]:
    '''Check if the user has earned any badges related to message usage.'''
    
    badges = []

    help_usage_count = db.admin.users.count_help_usage(username)
    if help_usage_count in gamification.rewards.Badges.HELP_USAGE:
        badges.append(gamification.rewards.Badges.HELP_USAGE[help_usage_count])

    return badges


@bp.route('/feedback', methods=['POST'])
@jwt_required()
def feedback():
    '''Log feedback for a message.'''
    username = get_jwt_identity()
    data = request.get_json()
    message_id = data['message_id']
    feedback = data['feedback']

    db.admin.messages.log_feedback(
        message_id=message_id,
        feedback=feedback,
        username=username,
    )

    rewards = []
    badges = []

    rewards.append(gamification.rewards.Actions.Messages.FEEDBACK)
    feedback_count = db.admin.users.count_feedbacks(username)

    if feedback_count in gamification.rewards.Badges.FEEDBACK:
        badges.append(gamification.rewards.Badges.FEEDBACK[feedback_count])

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response(True, rewards=rewards, badges=badges)


@bp.route('/error/explain', methods=['POST'])
@jwt_required()
def explain_error_message():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_EXPLAIN

    if not _check_coins(username, cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)
    
    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.explain_error_message(username, query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(username)

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response(answer=answer, id=answer_id, rewards=rewards, badges=badges)

@bp.route('/error/locate', methods=['POST'])
@jwt_required()
def locate_error_cause():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_LOCATE

    if not _check_coins(username, cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.locate_error_cause(username, query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(username)

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response(answer=answer, id=answer_id, rewards=rewards, badges=badges)

@bp.route('/error/example', methods=['POST'])
@jwt_required()
def provide_error_example():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_EXAMPLE

    if not _check_coins(username, cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.provide_error_example(username, query, exception)
    
    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(username)

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response(answer=answer, id=answer_id, rewards=rewards, badges=badges)

@bp.route('/error/fix', methods=['POST'])
@jwt_required()
def fix_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    cost = gamification.rewards.Actions.Messages.HELP_ERROR_FIX

    if not _check_coins(username, cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.fix_query(username, query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(username)

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response(answer=answer, id=answer_id, rewards=rewards, badges=badges)

@bp.route('/success/describe', methods=['POST'])
@jwt_required()
def describe_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    cost = gamification.rewards.Actions.Messages.HELP_SUCCESS_DESCRIBE

    if not _check_coins(username, cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    query = db.admin.queries.get(query_id)
    answer = llm.describe_my_query(username, query)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(username)

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response(answer=answer, id=answer_id, rewards=rewards, badges=badges)

@bp.route('/success/explain', methods=['POST'])
@jwt_required()
def explain_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    cost = gamification.rewards.Actions.Messages.HELP_SUCCESS_EXPLAIN

    if not _check_coins(username, cost):
        return responses.response(answer=NOT_ENOUGH_COINS_MESSAGE)

    query = db.admin.queries.get(query_id)
    answer = llm.explain_my_query(username, query)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    rewards = [cost]
    badges = _get_usage_badges(username)

    db.admin.users.add_rewards(username, *rewards, *badges)

    return responses.response(answer=answer, id=answer_id, rewards=rewards, badges=badges)