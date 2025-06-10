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

@bp.route('/set-teacher', methods=['POST'])
@jwt_required()
def set_teacher():
    """Set a user as teacher or not."""

    current_user = get_jwt_identity()
    data = request.get_json()
    username = data['username']
    value = data['value']

    if not db.admin.users.is_admin(current_user):
        return responses.response(False, message="Access denied: Admin privileges required.")

    return responses.response(
        db.admin.admin.set_teacher(current_user, username, value),
    )

@bp.route('/students', methods=['GET'])
@jwt_required()
def list_students():
    """List student status for a given teacher."""
    username = get_jwt_identity()
    data = request.args
    teacher = data.get('teacher')

    if not db.admin.users.is_teacher(username):
        return responses.response(False, message="Access denied: Teacher privileges required.")

    students = db.admin.teachers.get_students_status(teacher)

    return responses.response(True, data=students)

@bp.route('/assign-student', methods=['POST'])
@jwt_required()
def assign_student():
    """Assign a student to a teacher."""
    username = get_jwt_identity()
    data = request.get_json()
    student = data['student']
    teacher = data['teacher']
    value = data['value']

    if not db.admin.users.is_teacher(username):
        return responses.response(False, message="Access denied: Teacher privileges required.")

    if value:
        from dav_tools import messages
        messages.debug(f"Assigning student {student} to teacher {teacher}")
        db.admin.teachers.add_student(teacher, student)
    else:
        from dav_tools import messages
        messages.debug(f"Removing student {student} from teacher {teacher}")
        db.admin.teachers.remove_student(teacher, student)

    return responses.response(True)