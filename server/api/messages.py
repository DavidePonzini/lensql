'''This module handles message-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db, llm, gamification
from .util import responses

bp = Blueprint('message', __name__)


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

    db.admin.users.add_coins(username, gamification.Coins.HELP_FEEDBACK.value)

    return responses.response(True)


@bp.route('/error/explain', methods=['POST'])
@jwt_required()
def explain_error_message():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']
    
    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.explain_error_message(username, query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    db.admin.users.add_coins(username, gamification.Coins.HELP_ERROR_EXPLAIN.value)

    return responses.response(answer=answer, id=answer_id)

@bp.route('/error/locate', methods=['POST'])
@jwt_required()
def locate_error_cause():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.locate_error_cause(username, query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    db.admin.users.add_coins(username, gamification.Coins.HELP_ERROR_LOCATE.value)

    return responses.response(answer=answer, id=answer_id)

@bp.route('/error/example', methods=['POST'])
@jwt_required()
def provide_error_example():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.provide_error_example(username, query, exception)
    
    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    db.admin.users.add_coins(username, gamification.Coins.HELP_ERROR_EXAMPLE.value)

    return responses.response(answer=answer, id=answer_id)

@bp.route('/error/fix', methods=['POST'])
@jwt_required()
def fix_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.fix_query(username, query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    db.admin.users.add_coins(username, gamification.Coins.HELP_ERROR_FIX.value)

    return responses.response(answer=answer, id=answer_id)

@bp.route('/success/describe', methods=['POST'])
@jwt_required()
def describe_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    answer = llm.describe_my_query(username, query)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    db.admin.users.add_coins(username, gamification.Coins.HELP_SUCCESS_DESCRIBE.value)

    return responses.response(answer=answer, id=answer_id)

@bp.route('/success/explain', methods=['POST'])
@jwt_required()
def explain_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    answer = llm.explain_my_query(username, query)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    db.admin.users.add_coins(username, gamification.Coins.HELP_SUCCESS_EXPLAIN.value)

    return responses.response(answer=answer, id=answer_id)