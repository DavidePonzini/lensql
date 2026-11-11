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
        '''List exercises for a activity.'''

        user = db.admin.User(get_jwt_identity())
        
        activity_id = request.args.get('activity_id', type=str)

        if not activity_id:
            return responses.response(False, message=_('Activity ID is required.'))

        activity = db.admin.Activity(activity_id)

        if not activity.has_participant(user):
            return responses.response(False, message=_('You are not a participant of this activity.'))

        result = [{
            'exercise_id': exercise.exercise_id,
            'title': exercise.title,
            'request': exercise.request,
            'is_ai_generated': exercise.difficulty is not None,
            'learning_objectives': exercise.learning_objectives,
            'has_solution': len(exercise.solutions) > 0,
            'is_solved': exercise.has_been_solved_by_user(user),
            'is_hidden': exercise.is_hidden,
        } for exercise in activity.list_exercises(user)]

        return responses.response(True, data=result)

    def post(self):
        '''Add a new exercise.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        activity = db.admin.Activity(data['activity_id'])
        title = data['title']
        request_text = data['request']
        solutions = json.loads(data['solutions'])

        if not activity.has_owner(user):
            return responses.response(False, message=_('You are not authorized to add exercises to this activity.'))

        db.admin.Exercise.create(
            title=title,
            user=user,
            activity_id=activity.activity_id,
            request=request_text,
            solutions=solutions,
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

        activity = db.admin.Activity(exercise.activity_id)

        if not activity.has_owner(user):
            return responses.response(False, message=_('You are not authorized to edit this exercise.'))

        exercise.update(
            title=title,
            request=request_text,
            solutions=solutions,
        )

        return responses.response(True)

    def delete(self):
        '''Delete an exercise by its ID.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        exercise = db.admin.Exercise(int(data['exercise_id']))
        activity = db.admin.Activity(exercise.activity_id)

        if not activity.has_owner(user):
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

        activity = db.admin.Activity(exercise.activity_id)
        if not activity.has_participant(user):
            return responses.response(False, message=_('You are not a participant of this activity.'))

        objectives = exercise.learning_objectives

        return responses.response(True, data=objectives)
    
    def post(self):
        '''Set or unset a learning objective for an exercise.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        exercise = db.admin.Exercise(int(data['exercise_id']))
        objective_id = data['objective_id']
        value = data['value']

        activity = db.admin.Activity(exercise.activity_id)
        if not activity.has_owner(user):
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

    activity = db.admin.Activity(exercise.activity_id)
    if not activity.has_owner(user):
        return responses.response(False, message=_('You are not authorized to edit this exercise.'))

    exercise.set_hidden(value)

    return responses.response(True)

@bp.route('/init-activity', methods=['POST'])
@jwt_required()
def init_activity():
    '''Initialize the exercise activity.'''

    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    exercise = db.admin.Exercise(int(data['exercise_id']))

    activity = db.admin.Activity(exercise.activity_id)
    activity_str = activity.activity_str

    # Log the initialization of the activity for the exercise
    batch = db.admin.QueryBatch.log(user, exercise)
    db.admin.Query.log(
        query_batch=batch,
        sql_string='INIT ACTIVITY',
        search_path='BUILTIN',
        success=True,
        result='',
        query_type='BUILTIN',
        query_goal='BUILTIN',
    )

    def generate_results() -> Iterable[str]:
        database = db.users.get_database(user.username, activity.dbms)
        for query_result in database.execute_sql(activity_str, strip_comments=False):
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

    activity = db.admin.Activity(exercise.activity_id)
    if not activity.has_participant(user):
        return responses.response(False, message=_('You are not a participant of this activity.'))

    result = {
        'activity_id': exercise.activity_id,
        'title': exercise.title,
        'request': exercise.request,
        'attempts': exercise.count_attempts(user),
        'solutions': exercise.solutions,
        'last_query': exercise.get_last_query_batch_string_by_user(user),
    }

    return responses.response(True, data=result)
