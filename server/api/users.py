from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import _

from server import db
from .util import responses

bp = Blueprint('user', __name__)

@bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    user = db.admin.User(get_jwt_identity())

    if not user.exists():
        return responses.response(False)

    result = {
        'username': user.username,
        'is_teacher': user.is_teacher,
        'is_admin': user.is_admin,
        'xp': user.xp,
        'coins': user.coins,
    }
    
    return responses.response(True, **result)

@bp.route('/badges', methods=['GET'])
@jwt_required()
def get_user_badges():
    user = db.admin.User(get_jwt_identity())

    result = user.get_badges()

    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/stats/queries', methods=['GET'])
@jwt_required()
def get_query_stats():
    user = db.admin.User(get_jwt_identity())

    dataset_id = request.args.get('dataset_id', None, type=str) or None # required to handle empty string
    # if we have a dataset ID, load the dataset string
    exercise_id = request.args.get('exercise_id', None, type=int)
    is_teacher = request.args.get('is_teacher', '0') == '1'

    # if we have an exercise, then we have a dataset
    #   (ignore dataset ID passed as argument, just to be safe)
    if exercise_id is not None:
        dataset_id = db.admin.Exercise(exercise_id).dataset_id

    if dataset_id is None:
        # if no dataset ID is provided, the user is querying their own stats
        result = user.get_query_stats(dataset_id=None, exercise_id=None)
    else:
        dataset = db.admin.Dataset(dataset_id)

        if not dataset.has_participant(user):
            return responses.response(False, message=_("User is not a participant in the specified dataset."))

        # ensure user is actually a teacher
        is_teacher &= dataset.has_teacher(user)

        result = user.get_query_stats(
            dataset_id=dataset.dataset_id,
            exercise_id=exercise_id,
            is_teacher=is_teacher
        )

    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/stats/unique_queries', methods=['GET'])
@jwt_required()
def get_unique_queries_count():
    user = db.admin.User(get_jwt_identity())

    count = user.count_unique_queries()
    return responses.response(True, data=count)

@bp.route('/stats/messages', methods=['GET'])
@jwt_required()
def get_message_stats():
    user = db.admin.User(get_jwt_identity())

    dataset_id = request.args.get('dataset_id', None, type=str) or None # required to handle empty string
    exercise_id = request.args.get('exercise_id', None, type=int)
    is_teacher = request.args.get('is_teacher', '0') == '1'

    # if we have an exercise, then we have a dataset
    #   (ignore dataset ID passed as argument, just to be safe)
    if exercise_id is not None:
        dataset_id = db.admin.Exercise(exercise_id).dataset_id

    if dataset_id is None:
        # if no dataset ID is provided, the user is querying their own stats
        result = user.get_message_stats()
    else:
        dataset = db.admin.Dataset(dataset_id)
        if not dataset.has_participant(user):
            return responses.response(False, message=_("User is not a participant in the specified dataset."))

        # ensure user is actually a teacher
        is_teacher &= dataset.has_teacher(user)

        result = user.get_message_stats(
            dataset_id=dataset.dataset_id,
            exercise_id=exercise_id,
            is_teacher=is_teacher
        )

    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/stats/errors', methods=['GET'])
@jwt_required()
def get_error_stats():
    user = db.admin.User(get_jwt_identity())

    dataset_id = request.args.get('dataset_id', None, type=str) or None # required to handle empty string
    exercise_id = request.args.get('exercise_id', None, type=int)
    is_teacher = request.args.get('is_teacher', '0') == '1'

    # if we have an exercise, then we have a dataset
    #   (ignore dataset ID passed as argument, just to be safe)
    if exercise_id is not None:
        dataset_id = db.admin.Exercise(exercise_id).dataset_id

    if dataset_id is None:
        # if no dataset ID is provided, the user is querying their own stats
        result = user.get_error_stats()
    else:
        dataset = db.admin.Dataset(dataset_id)

        if not dataset.has_participant(user):
            return responses.response(False, message=_("User is not a participant in the specified dataset."))

        # Ensure user is actually a teacher
        is_teacher &= dataset.has_teacher(user)
        
        result = user.get_error_stats(
            dataset_id=dataset.dataset_id,
            exercise_id=exercise_id,
            is_teacher=is_teacher
        )

    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/set-teacher', methods=['POST'])
@jwt_required()
def set_teacher_status():
    '''Set the teacher status for the current user.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    is_teacher = data['is_teacher']

    user.set_teacher_status(is_teacher)
    
    return responses.response(True)