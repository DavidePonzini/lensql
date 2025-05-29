'''This module handles message-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db, llm
from .util import responses

message_bp = Blueprint('message', __name__)


@message_bp.route('/feedback', methods=['POST'])
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

    return responses.response(True)


@message_bp.route('/error/explain', methods=['POST'])
@jwt_required()
def explain_error_message():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']
    
    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.explain_error_message(query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return responses.response(answer=answer, id=answer_id)

@message_bp.route('/error/locate', methods=['POST'])
@jwt_required()
def locate_error_cause():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.locate_error_cause(query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return responses.response(answer=answer, id=answer_id)

@message_bp.route('/error/example', methods=['POST'])
@jwt_required()
def provide_error_example():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    # answer = llm.provide_error_example(query, exception)
    answer = responses.NOT_IMPLEMENTED
    
    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return responses.response(answer=answer, id=answer_id)

@message_bp.route('/error/fix', methods=['POST'])
@jwt_required()
def fix_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    exception = db.admin.queries.get_result(query_id)
    answer = llm.fix_query(query, exception)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return responses.response(answer=answer, id=answer_id)

@message_bp.route('/success/describe', methods=['POST'])
@jwt_required()
def describe_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    answer = llm.describe_my_query(query)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return responses.response(answer=answer, id=answer_id)

@message_bp.route('/success/explain', methods=['POST'])
@jwt_required()
def explain_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db.admin.queries.get(query_id)
    answer = llm.explain_my_query(query)

    answer_id = db.admin.messages.log(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return responses.response(answer=answer, id=answer_id)