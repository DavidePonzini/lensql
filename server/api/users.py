from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db
from .util import responses

bp = Blueprint('user', __name__)

@bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    username = get_jwt_identity()

    result = db.admin.users.get_info(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, **result)

@bp.route('/stats/queries', methods=['GET'])
@jwt_required()
def get_query_stats():
    username = get_jwt_identity()

    result = db.admin.users.get_query_stats(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/stats/unique_queries', methods=['GET'])
@jwt_required()
def get_unique_queries_count():
    username = get_jwt_identity()

    count = db.admin.users.get_unique_queries_count(username)
    return responses.response(True, data=count)

@bp.route('/stats/messages', methods=['GET'])
@jwt_required()
def get_message_stats():
    username = get_jwt_identity()

    result = db.admin.users.get_message_stats(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/stats/errors', methods=['GET'])
@jwt_required()
def get_error_stats():
    username = get_jwt_identity()

    result = db.admin.users.get_error_stats(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)