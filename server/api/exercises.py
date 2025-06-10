'''This module handles exercise-related endpoints for the API.'''

import json
from typing import Iterable
from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity

from .util import responses
from server import db

exercise_bp = Blueprint('exercise', __name__)

class ExerciseAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''Get a specific exercise by its ID.'''

        username = get_jwt_identity()
        exercise_id = request.args.get('id')
        result = db.admin.exercises.get(exercise_id, username)
        return responses.response(True, data=result)

    def post(self):
        '''Add a new exercise.'''

        data = request.get_json()
        title = data['title']
        request_text = data['request']
        dataset_id = data['dataset_id'] or None
        expected_answer = data['expected_answer']

        db.admin.exercises.create(
            title=title,
            request=request_text,
            dataset_id=dataset_id,
            expected_answer=expected_answer,
            is_ai_generated=False
        )
        return responses.response(True)

    def put(self):
        '''Edit an existing exercise.'''

        data = request.get_json()
        exercise_id = data['exercise_id']
        title = data['title']
        request_text = data['request']
        dataset_id = data['dataset_id'] or None
        expected_answer = data['expected_answer']

        db.admin.exercises.update(
            exercise_id=exercise_id,
            title=title,
            request=request_text,
            dataset_id=dataset_id,
            expected_answer=expected_answer
        )
        return responses.response(True)

    def delete(self):
        '''Delete an exercise by its ID.'''

        data = request.get_json()
        exercise_id = data['exercise_id']
        db.admin.exercises.delete(exercise_id)
        return responses.response(True)

# Register all methods (GET, POST, PUT, DELETE) on /
#   Note: trailing slash causes nginx to redirect, leading to CORS error
exercise_bp.add_url_rule('', view_func=ExerciseAPI.as_view('exercise_api'))

@exercise_bp.route('/list', methods=['GET'])
@jwt_required()
def get_all_exercises():
    '''Get a list of all exercises.'''

    username = get_jwt_identity()

    exercises = db.admin.exercises.list_all(username)
    return responses.response(True, data=exercises)

@exercise_bp.route('/assign', methods=['POST'])
@jwt_required()
def assign():
    '''Assign or unassign an exercise to a student.'''

    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']
    student_id = data['student_id']
    value = data['value']

    if value:
        db.admin.exercises.assign(
            teacher=username,
            exercise_id=exercise_id,
            student=student_id
        )
    else:
        db.admin.exercises.unassign(
            teacher=username,
            exercise_id=exercise_id,
            student=student_id
        )

    return responses.response(True)

@exercise_bp.route('/objective', methods=['POST'])
@jwt_required()
def set_learning_objective():
    '''Set learning objective for an exercise.'''

    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']
    objective = data['objective']
    value = data['value']

    if value:
        db.admin.exercises.set_learning_objective(
            teacher=username,
            exercise_id=exercise_id,
            objective=objective
        )
    else:
        db.admin.exercises.unset_learning_objective(
            teacher=username,
            exercise_id=exercise_id,
            objective=objective
        )

    return responses.response(True)


@exercise_bp.route('/list-objectives', methods=['GET'])
@jwt_required()
def list_learning_objectives():
    '''List learning objectives for an exercise.'''

    username = get_jwt_identity()
    exercise_id = request.args.get('exercise_id')

    objectives = db.admin.exercises.list_learning_objectives(exercise_id)

    return responses.response(True, data=objectives)

@exercise_bp.route('/init-dataset', methods=['POST'])
@jwt_required()
def init_dataset():
    '''Initialize the exercise dataset.'''

    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    dataset = db.admin.exercises.get_dataset(exercise_id)

    def generate_results() -> Iterable[str]:
        for query_result in db.users.queries.execute(username=username, query_str=dataset, strip_comments=False):
            yield json.dumps({
                'success': query_result.success,
                'builtin': True,
                'query': query_result.query,
                'type': query_result.query_type,
                'data': query_result.result,
                'id': None,
            }) + '\n'  # Important: one JSON object per line

    return responses.streaming_response(generate_results())
