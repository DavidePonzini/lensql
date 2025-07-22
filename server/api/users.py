from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db
from .util import responses

bp = Blueprint('user', __name__)

@bp.route('/info', methods=['GET'])
@jwt_required()
def get_user_info():
    username = get_jwt_identity()

    result = db.admin.users.get_info(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, **result)

@bp.route('/stats/queries', methods=['GET'])
@jwt_required()
def get_query_stats():
    username = get_jwt_identity()
    class_id = request.args.get('class_id', None)
    exercise_id = request.args.get('exercise_id', None, type=int)

    from dav_tools import messages
    messages.debug(f'Query stats for user "{username}", class_id: "{class_id}", exercise_id: "{exercise_id}"', request.args)

    # if we have an exercise, then we have a class
    #   (ignore class ID passed as argument, just to be safe)
    if exercise_id is not None:
        class_id = db.admin.exercises.get_class(exercise_id)

    if class_id is None:
        # if no class ID is provided, the user is querying their own stats
        result = db.admin.users.get_query_stats(username)
    else:
        if not db.admin.classes.has_participant(username=username, class_id=class_id):
            return responses.response(False, message="User is not a participant in the specified class.")

        is_teacher = db.admin.classes.has_teacher(username=username, class_id=class_id)

        result = db.admin.users.get_query_stats(
            username=username,
            class_id=class_id,
            exercise_id=exercise_id,
            is_teacher=is_teacher
        )

    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/stats/unique_queries', methods=['GET'])
@jwt_required()
def get_unique_queries_count():
    username = get_jwt_identity()

    count = db.admin.users.get_unique_queries_count(username)
    return responses.response(True, data=count)

@bp.route('/stats/messages', methods=['GET'])
@jwt_required()
def get_message_stats():
    username = get_jwt_identity()
    class_id = request.args.get('class_id', None)
    exercise_id = request.args.get('exercise_id', None, type=int)

    from dav_tools import messages
    messages.debug(f'Message stats for user "{username}", class_id: "{class_id}", exercise_id: "{exercise_id}"', request.args)

    # if we have an exercise, then we have a class
    #   (ignore class ID passed as argument, just to be safe)
    if exercise_id is not None:
        class_id = db.admin.exercises.get_class(exercise_id)

    if class_id is None:
        # if no class ID is provided, the user is querying their own stats
        result = db.admin.users.get_message_stats(username)
    else:
        if not db.admin.classes.has_participant(username=username, class_id=class_id):
            return responses.response(False, message="User is not a participant in the specified class.")

        is_teacher = db.admin.classes.has_teacher(username=username, class_id=class_id)

        result = db.admin.users.get_message_stats(
            username=username,
            class_id=class_id,
            exercise_id=exercise_id,
            is_teacher=is_teacher
        )

    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)

@bp.route('/stats/errors', methods=['GET'])
@jwt_required()
def get_error_stats():
    username = get_jwt_identity()

    result = db.admin.users.get_error_stats(username)
    if result is None:
        return responses.response(False)
    
    return responses.response(True, data=result)