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
        'ai_generation_credits': user.ai_generation_credits,
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

    activity_id = request.args.get('activity_id', None, type=str) or None # required to handle empty string
    # if we have a activity ID, load the activity string
    exercise_id = request.args.get('exercise_id', None, type=int)
    is_teacher = request.args.get('is_teacher', '0') == '1'

    # if we have an exercise, then we have a activity
    #   (ignore activity ID passed as argument, just to be safe)
    if exercise_id is not None:
        activity_id = db.admin.Exercise(exercise_id).activity_id

    if activity_id is None:
        # if no activity ID is provided, the user is querying their own stats
        result = user.get_query_stats(activity_id=None, exercise_id=None)
    else:
        activity = db.admin.Activity(activity_id)

        if not activity.has_participant(user):
            return responses.response(False, message=_("User is not a participant in the specified activity."))

        # ensure user owns the activity if querying as teacher
        is_teacher &= activity.has_owner(user)

        result = user.get_query_stats(
            activity_id=activity.activity_id,
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

    activity_id = request.args.get('activity_id', None, type=str) or None # required to handle empty string
    exercise_id = request.args.get('exercise_id', None, type=int)
    is_teacher = request.args.get('is_teacher', '0') == '1'

    # if we have an exercise, then we have a activity
    #   (ignore activity ID passed as argument, just to be safe)
    if exercise_id is not None:
        activity_id = db.admin.Exercise(exercise_id).activity_id

    if activity_id is None:
        # if no activity ID is provided, the user is querying their own stats
        result = user.get_message_stats()
    else:
        activity = db.admin.Activity(activity_id)
        if not activity.has_participant(user):
            return responses.response(False, message=_("User is not a participant in the specified activity."))

        # ensure user owns the activity if querying as teacher
        is_teacher &= activity.has_owner(user)

        result = user.get_message_stats(
            activity_id=activity.activity_id,
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

    activity_id = request.args.get('activity_id', None, type=str) or None # required to handle empty string
    exercise_id = request.args.get('exercise_id', None, type=int)
    is_teacher = request.args.get('is_teacher', '0') == '1'

    # if we have an exercise, then we have a activity
    #   (ignore activity ID passed as argument, just to be safe)
    if exercise_id is not None:
        activity_id = db.admin.Exercise(exercise_id).activity_id

    if activity_id is None:
        # if no activity ID is provided, the user is querying their own stats
        result = user.get_error_stats()
    else:
        activity = db.admin.Activity(activity_id)

        if not activity.has_participant(user):
            return responses.response(False, message=_("User is not a participant in the specified activity."))

        # ensure user owns the activity if querying as teacher
        is_teacher &= activity.has_owner(user)
        
        result = user.get_error_stats(
            activity_id=activity.activity_id,
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

@bp.route('/admin/generation-credits', methods=['POST'])
@jwt_required()
def set_generation_credits():
    admin = db.admin.User(get_jwt_identity())
    if not admin.is_admin:
        return responses.response(False, message=_('You do not have permission to perform this action.'))
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return responses.response(False, message=_('Invalid request.'))
    username = data.get('username')
    credits = data.get('ai_generation_credits')
    if not isinstance(username, str) or not username.strip():
        return responses.response(False, message=_('User does not exist.'))
    if type(credits) is not int or not 0 <= credits <= 2147483647:
        return responses.response(False, message=_('Credits must be a non-negative integer.'))
    user = db.admin.User(username.strip())
    if not user.exists():
        return responses.response(False, message=_('User does not exist.'))
    user.set_ai_generation_credits(credits)
    return responses.response(True, ai_generation_credits=credits)
