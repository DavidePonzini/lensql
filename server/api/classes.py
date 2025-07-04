'''This module handles classes-related endpoints for the API.'''

from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity

from server import db
from .util import responses

bp = Blueprint('classes', __name__)


class ClassesAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''List classes visible to the user.'''

        username = get_jwt_identity()
        result = db.admin.classes.list_classes(username)
        return responses.response(True, data=result)

    def post(self):
        '''Create a new class.'''

        username = get_jwt_identity()
        data = request.get_json()
        title = data['title']
        dataset = data['dataset']

        class_id = db.admin.classes.create(title, dataset=dataset)
        db.admin.classes.join(username, class_id)
        db.admin.classes.make_teacher(username, class_id)

        return responses.response(True)

    def put(self):
        '''Rename a class.'''

        data = request.get_json()
        class_id = data['class_id']
        title = data['title']
        dataset = data['dataset']

        db.admin.classes.update(
            class_id=class_id,
            title=title,
            dataset=dataset
        )

        return responses.response(True)

# Register all methods (GET, POST, PUT, DELETE) on /
#   Note: trailing slash causes nginx to redirect, leading to CORS error
bp.add_url_rule('', view_func=ClassesAPI.as_view('classes_api'))

@bp.route('/get', methods=['GET'])
@jwt_required()
def get_class():
    '''Get a class by its ID.'''
    username = get_jwt_identity()
    data = request.args
    class_id = data['class_id']

    if not db.admin.classes.exists(class_id):
        return responses.response(False, message='Class does not exist.')

    if not db.admin.classes.has_participant(class_id=class_id, username=username):
        return responses.response(False, message='You do not have access to this class.')

    result = db.admin.classes.get(class_id)

    return responses.response(True, data=result)

@bp.route('/join', methods=['POST'])
@jwt_required()
def join_class():
    '''Join a class by its ID.'''
    username = get_jwt_identity()
    data = request.get_json()
    class_id = str(data['class_id']).strip().upper()    # sanitize join code

    if not db.admin.classes.exists(class_id):
        return responses.response(False, message='Class does not exist.')
    
    db.admin.classes.join(username, class_id)

    return responses.response(True)

@bp.route('/leave', methods=['POST'])
@jwt_required()
def leave_class():
    '''Leave a class by its ID.'''
    username = get_jwt_identity()
    data = request.get_json()
    class_id = data['class_id']

    if db.admin.classes.leave(username, class_id):
        return responses.response(True)
    else:
        return responses.response(False, message='You cannot leave this class, as you are a teacher and it has data associated with it.')


@bp.route('/is-teacher', methods=['GET'])
@jwt_required()
def is_teacher():
    '''Check if the user is a teacher of a class.'''
    username = get_jwt_identity()
    data = request.args
    class_id = data.get('class_id')

    result = db.admin.classes.has_teacher(username, class_id)

    return responses.response(True, is_teacher=result)

@bp.route('/set-teacher', methods=['POST'])
@jwt_required()
def set_teacher():
    '''Set a user as a teacher of a class.'''
    current_username = get_jwt_identity()
    data = request.get_json()
    class_id = data['class_id']
    username = data['username']
    value = data['value']

    if not db.admin.classes.has_teacher(current_username, class_id):
        return responses.response(False, message='You are not a teacher of this class.')

    if current_username == username:
        return responses.response(False, message='You cannot set yourself as a teacher of this class.')

    if value:
        db.admin.classes.make_teacher(username, class_id)
    else:
        db.admin.classes.remove_teacher(username, class_id)

    return responses.response(True)


@bp.route('/members', methods=['GET'])
@jwt_required()
def get_members():
    '''Get the members of a class.'''
    username = get_jwt_identity()
    data = request.args
    class_id = data.get('class_id')

    if not db.admin.classes.has_teacher(username, class_id):
        return responses.response(False, message='You are not a teacher of this class.')
    
    members = db.admin.classes.get_members(class_id)

    return responses.response(True, members=members)
