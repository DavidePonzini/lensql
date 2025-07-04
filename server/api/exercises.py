'''This module handles exercise-related endpoints for the API.'''

import json
from typing import Iterable
from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity

from .util import responses
from server import db

bp = Blueprint('exercise', __name__)

class ExerciseAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''List exercises for a class.'''

        username = get_jwt_identity()
        class_id = request.args.get('class_id')

        if not db.admin.classes.has_participant(username, class_id):
            return responses.response(False, message='You are not a participant of this class.')
        
        if db.admin.classes.has_teacher(username, class_id):
            # Teachers can see all exercises
            result = db.admin.exercises.get_from_class(username=username, class_id=class_id, include_hidden=True)
        else:
            result = db.admin.exercises.get_from_class(username=username, class_id=class_id)
        
        return responses.response(True, data=result)

    def post(self):
        '''Add a new exercise.'''

        data = request.get_json()
        title = data['title']
        class_id = data['class_id']
        request_text = data['request']
        solution = data['solution']

        db.admin.exercises.create(
            title=title,
            class_id=class_id,
            request=request_text,
            solution=solution,
            is_ai_generated=False
        )

        return responses.response(True)

    def put(self):
        '''Edit an existing exercise.'''

        data = request.get_json()
        exercise_id = data['exercise_id']
        title = data['title']
        request_text = data['request']
        solution = data['solution']

        db.admin.exercises.update(
            exercise_id=exercise_id,
            title=title,
            request=request_text,
            solution=solution
        )
        return responses.response(True)

    def delete(self):
        '''Delete an exercise by its ID.'''

        data = request.get_json()
        exercise_id = data['exercise_id']
        
        success = db.admin.exercises.delete(exercise_id)
        
        if not success:
            return responses.response(False, message='Cannot delete exercise. There are queries associated with it.')
        return responses.response(True)

# Register all methods (GET, POST, PUT, DELETE) on /
#   Note: trailing slash causes nginx to redirect, leading to CORS error
bp.add_url_rule('', view_func=ExerciseAPI.as_view('exercise_api'))

class ObjectivesAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''List learning objectives for an exercise.'''

        exercise_id = request.args.get('exercise_id')

        objectives = db.admin.exercises.list_learning_objectives(exercise_id)

        return responses.response(True, data=objectives)
    
    def post(self):
        '''Set or unset a learning objective for an exercise.'''

        username = get_jwt_identity()
        data = request.get_json()
        exercise_id = data['exercise_id']
        objective = data['objective']
        value = data['value']

        class_id = db.admin.exercises.get_class(exercise_id)
        if not db.admin.classes.has_teacher(username, class_id):
            return responses.response(False, message='You are not authorized to set learning objectives for this exercise.')

        if value:
            db.admin.exercises.set_learning_objective(
                exercise_id=exercise_id,
                objective=objective
            )
        else:
            db.admin.exercises.unset_learning_objective(
                exercise_id=exercise_id,
                objective=objective
            )

        return responses.response(True)

# Register all methods (GET, POST) on /learning-objectives
bp.add_url_rule('/objectives', view_func=ObjectivesAPI.as_view('objectives_api'))


@bp.route('/hide', methods=['POST'])
@jwt_required()
def hide_exercise():
    '''Hide an exercise from students.'''

    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']
    value = data['value']

    class_id = db.admin.exercises.get_class(exercise_id)
    if not db.admin.classes.has_teacher(username, class_id):
        return responses.response(False, message='You are not authorized to edit this exercise.')

    if value:
        db.admin.exercises.hide(exercise_id)
    else:
        db.admin.exercises.unhide(exercise_id)

    return responses.response(True)

@bp.route('/init-dataset', methods=['POST'])
@jwt_required()
def init_dataset():
    '''Initialize the exercise dataset.'''

    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    class_id = db.admin.exercises.get_class(exercise_id)
    dataset = db.admin.classes.get_dataset(class_id)

    def generate_results() -> Iterable[str]:
        for query_result in db.users.queries.execute(username=username, query_str=dataset, strip_comments=False):
            yield json.dumps({
                'success': query_result.success,
                'builtin': True,
                'query': query_result.query.query,
                'type': query_result.data_type,
                'data': query_result.result_html,
                'id': None,
            }) + '\n'  # Important: one JSON object per line

    return responses.streaming_response(generate_results())

@bp.route('/get', methods=['GET'])
@jwt_required()
def get_exercise():
    '''Get a specific exercise by its ID.'''

    username = get_jwt_identity()
    exercise_id = request.args.get('exercise_id')

    result = db.admin.exercises.get_data(exercise_id=exercise_id, username=username)

    if not result:
        return responses.response(False, message='Exercise not found.')

    return responses.response(True, data=result)

@bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_exercise():
    '''Submit an exercise.'''

    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']
    value = data['value']

    if value:
        if not db.admin.exercises.submit(username=username, exercise_id=exercise_id):
            return responses.response(False, message='Failed to submit exercise.')
        return responses.response(True)
    else:
        if not db.admin.exercises.unsubmit(username=username, exercise_id=exercise_id):
            return responses.response(False, message='Failed to unsubmit exercise.')
        return responses.response(True)
