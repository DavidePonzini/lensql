'''This module handles assignment-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db
from .util import responses

assignment_bp = Blueprint('assignment', __name__)


@assignment_bp.route('/list', methods=['GET'])
@jwt_required()
def get_assignments():
    '''Get a list of assignments visible to the user.'''
    username = get_jwt_identity()

    assignments = db.admin.assignments.list_all(username)

    return responses.response(True, data=assignments)

@assignment_bp.route('/students', methods=['GET'])
@jwt_required()
def get_assignment_students():
    '''Get whether each student is assigned to an exercise.'''
    username = get_jwt_identity()
    data = request.args
    exercise_id = data.get('exercise_id')

    students = db.admin.assignments.get_students(username, exercise_id)

    return responses.response(True, students=students)


@assignment_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_exercise():
    '''Submit an assignment'''
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    db.admin.assignments.submit(username, exercise_id)

    return responses.response(True)

@assignment_bp.route('/unsubmit', methods=['POST'])
@jwt_required()
def unsubmit_exercise():
    '''Unsubmit an assignment'''
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    db.admin.assignments.unsubmit(username, exercise_id)

    return responses.response(True)
