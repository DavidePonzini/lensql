from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db
from .util import responses

user_bp = Blueprint('user', __name__)

@user_bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    username = get_jwt_identity()

    result = db.admin.users.get_info(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, **result)

@user_bp.route('/learning-stats', methods=['GET'])
@jwt_required()
def get_learning_stats():
    username = get_jwt_identity()

    result = db.admin.users.get_learning_stats(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)