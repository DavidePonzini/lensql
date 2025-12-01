'''This module handles exercise-related endpoints for the API.'''

import json
from typing import Iterable
from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import _

from .util import responses
from server import db

bp = Blueprint('exercise', __name__)

class ExerciseAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''List exercises for a dataset.'''

        user = db.admin.User(get_jwt_identity())
        
        dataset_id = request.args.get('dataset_id', type=str)

        if not dataset_id:
            return responses.response(False, message=_('Dataset ID is required.'))

        dataset = db.admin.Dataset(dataset_id)

        if not dataset.has_participant(user):
            return responses.response(False, message=_('You are not a participant of this dataset.'))

        result = [{
            'exercise_id': exercise.exercise_id,
            'title': exercise.title,
            'request': exercise.request,
            'is_ai_generated': exercise.is_ai_generated,
            'learning_objectives': exercise.learning_objectives,
            'is_solved': exercise.has_been_solved_by_user(user),
            'is_hidden': exercise.is_hidden,
            'search_path': exercise.search_path,
        } for exercise in dataset.list_exercises(user)]

        return responses.response(True, data=result)

    def post(self):
        '''Add a new exercise.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        dataset = db.admin.Dataset(data['dataset_id'])
        title = data['title']
        request_text = data['request']
        solutions = json.loads(data['solutions'])
        search_path = data['search_path'] or 'public'   # Handle empty string

        if not dataset.has_teacher(user):
            return responses.response(False, message=_('You are not authorized to add exercises to this dataset.'))

        db.admin.Exercise.create(
            title=title,
            user=user,
            dataset_id=dataset.dataset_id,
            request=request_text,
            solutions=solutions,
            search_path=search_path
        )

        return responses.response(True)

    def put(self):
        '''Edit an existing exercise.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        exercise = db.admin.Exercise(int(data['exercise_id']))
        title = data['title']
        request_text = data['request']
        solutions = json.loads(data['solutions'])
        search_path = data['search_path'] or 'public'   # Handle empty string

        dataset = db.admin.Dataset(exercise.dataset_id)

        if not dataset.has_teacher(user):
            return responses.response(False, message=_('You are not authorized to edit this exercise.'))

        exercise.update(
            title=title,
            request=request_text,
            solutions=solutions,
            search_path=search_path
        )

        return responses.response(True)

    def delete(self):
        '''Delete an exercise by its ID.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        exercise = db.admin.Exercise(int(data['exercise_id']))
        dataset = db.admin.Dataset(exercise.dataset_id)

        if not dataset.has_teacher(user):
            return responses.response(False, message=_('You are not authorized to delete this exercise.'))
        
        success = exercise.delete()
        
        if not success:
            return responses.response(False, message=_('Cannot delete exercise. There are queries associated with it.'))
        return responses.response(True)

# Register all methods (GET, POST, PUT, DELETE) on /
#   Note: trailing slash causes nginx to redirect, leading to CORS error
bp.add_url_rule('', view_func=ExerciseAPI.as_view('exercise_api'))

class LearningObjectivesAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''List learning objectives for an exercise.'''

        user = db.admin.User(get_jwt_identity())

        exercise_id = request.args.get('exercise_id', type=int)
        if exercise_id is None:
            return responses.response(False, message=_('Exercise ID is required.'))
        exercise = db.admin.Exercise(exercise_id)

        dataset = db.admin.Dataset(exercise.dataset_id)
        if not dataset.has_participant(user):
            return responses.response(False, message=_('You are not a participant of this dataset.'))

        objectives = exercise.learning_objectives

        return responses.response(True, data=objectives)
    
    def post(self):
        '''Set or unset a learning objective for an exercise.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        exercise = db.admin.Exercise(int(data['exercise_id']))
        objective_id = data['objective_id']
        value = data['value']

        dataset = db.admin.Dataset(exercise.dataset_id)
        if not dataset.has_teacher(user):
            return responses.response(False, message=_('You are not authorized to set learning objectives for this exercise.'))
        
        exercise.set_learning_objective(
            objective_id=objective_id,
            is_set=value
        )

        return responses.response(True)

# Register all methods (GET, POST) on /learning-objectives
bp.add_url_rule('/objectives', view_func=LearningObjectivesAPI.as_view('learning_objectives_api'))


@bp.route('/hide', methods=['POST'])
@jwt_required()
def hide_exercise():
    '''Hide an exercise from students.'''

    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))
    value = data['value']

    dataset = db.admin.Dataset(exercise.dataset_id)
    if not dataset.has_teacher(user):
        return responses.response(False, message=_('You are not authorized to edit this exercise.'))

    exercise.set_hidden(value)

    return responses.response(True)

@bp.route('/init-dataset', methods=['POST'])
@jwt_required()
def init_dataset():
    '''Initialize the exercise dataset.'''

    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))

    dataset = db.admin.Dataset(exercise.dataset_id)
    dataset_str = dataset.dataset_str

    def generate_results() -> Iterable[str]:
        for query_result in db.users.queries.execute(username=user.username, query_str=dataset_str, strip_comments=False):
            yield json.dumps({
                'success': query_result.success,
                'builtin': True,
                'query': query_result.query.query,
                'type': query_result.data_type,
                'data': query_result.result_html,
                'id': None,
            }) + '\n'  # Important: one JSON object per line

    return responses.streaming_response(generate_results())

@bp.route('/get/<exercise_id>', methods=['GET'])
@jwt_required()
def get_exercise(exercise_id):
    '''Get a specific exercise by its ID.'''

    user = db.admin.User(get_jwt_identity())

    exercise = db.admin.Exercise(int(exercise_id))

    dataset = db.admin.Dataset(exercise.dataset_id)
    if not dataset.has_participant(user):
        return responses.response(False, message=_('You are not a participant of this dataset.'))

    result = {
        'dataset_id': exercise.dataset_id,
        'title': exercise.title,
        'request': exercise.request,
        'attempts': exercise.count_attempts(user),
        'search_path': exercise.search_path,
        'solutions': exercise.solutions,
    }

    import dav_tools

    dav_tools.messages.debug(f'Exercise get result: {result}')

    return responses.response(True, data=result)
