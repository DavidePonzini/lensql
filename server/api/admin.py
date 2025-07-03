'''This module provides admin functionalities for managing users in the system.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db
from .util import responses

bp = Blueprint('admin', __name__)


@bp.route('/users', methods=['GET'])
@jwt_required()
def list_all_users():
    """List all users in the database."""

    username = get_jwt_identity()

    if not db.admin.users.is_admin(username):
        return responses.response(False, message="Access denied: Admin privileges required.")
    
    users = db.admin.admin.list_all_users(username)

    return responses.response(True, data=users)

@bp.route('/set-admin', methods=['POST'])
@jwt_required()
def set_admin():
    """Set a user as admin or not."""

    current_user = get_jwt_identity()
    data = request.get_json()
    username = data['username']
    value = data['value']

    if not db.admin.users.is_admin(current_user):
        return responses.response(False, message="Access denied: Admin privileges required.")

    return responses.response(
        db.admin.admin.set_admin(current_user, username, value),
    )

@bp.route('/datasets', methods=['GET'])
@jwt_required()
def list_datasets():
    """List dataset assignment status for a given teacher."""
    
    username = get_jwt_identity()
    
    data = request.args
    teacher = data.get('teacher')

    if not db.admin.users.is_teacher(username):
        return responses.response(False, message="Access denied: Teacher privileges required.")

    datasets = db.admin.teachers.get_datasets_status(teacher)

    return responses.response(True, data=datasets)

@bp.route('/assign-dataset', methods=['POST'])
@jwt_required()
def assign_dataset():
    """Assign a dataset to a teacher."""
    
    username = get_jwt_identity()

    data = request.get_json()
    teacher = data['teacher']
    dataset = data['dataset']
    value = data['value']

    if not db.admin.users.is_teacher(username):
        return responses.response(False, message="Access denied: Teacher privileges required.")

    if value:
        db.admin.teachers.assign_dataset(teacher, dataset)
    else:
        db.admin.teachers.remove_dataset(teacher, dataset)

    return responses.response(True)
