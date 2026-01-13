'''This module handles dataset-related endpoints for the API.'''

from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import _

from server import db, gamification
from .util import responses

bp = Blueprint('datasets', __name__)


class DatasetsAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''List datasets visible to the user.'''

        user = db.admin.User(get_jwt_identity())

        result = user.list_datasets()

        return responses.response(True, data=result)

    def post(self):
        '''Create a new dataset.'''

        user = db.admin.User(get_jwt_identity())
    
        data = request.get_json()
        title = data['title']
        description = data['description']
        dataset_str = data['dataset']

        dataset = db.admin.Dataset.create(title=title, description=description, dataset_str=dataset_str)
        dataset.add_participant(user)
        dataset.set_owner_status(user, True)

        return responses.response(True)

    def put(self):
        '''Rename a dataset.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        dataset_id = data['dataset_id']
        title = data['title']
        description = data['description']
        dataset_str = data['dataset']

        dataset = db.admin.Dataset(dataset_id)
        if not dataset.has_owner(user):
            return responses.response(False, message=_('You are not authorized to modify this dataset.'))

        dataset.update(title=title, description=description, dataset_str=dataset_str)

        return responses.response(True)

# Register all methods (GET, POST, PUT, DELETE) on /
#   Note: trailing slash causes nginx to redirect, leading to CORS error
bp.add_url_rule('', view_func=DatasetsAPI.as_view('datasets_api'))

@bp.route('/get/<dataset_id>', methods=['GET'])
@jwt_required()
def get_dataset(dataset_id):
    '''Get a dataset by its ID.'''
    user = db.admin.User(get_jwt_identity())

    dataset = db.admin.Dataset(dataset_id)

    if not dataset.exists():
        return responses.response(False, message='Dataset does not exist.')
    if not dataset.has_participant(user):
        return responses.response(False, message=_('You do not have access to this dataset.'))

    result = {
        'title': dataset.name,
        'description': dataset.description,
        'dataset_str': dataset.dataset_str,
    }

    return responses.response(True, data=result)

@bp.route('/join', methods=['POST'])
@jwt_required()
def join_dataset():
    '''Join a dataset by its ID.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    dataset_id = str(data['dataset_id']).strip().upper()    # sanitize join code

    dataset = db.admin.Dataset(dataset_id)

    if not dataset.exists():
        return responses.response(False, message=_('Dataset does not exist.'))
    dataset.add_participant(user)

    badges = []

    joined_datasets = user.count_all_datasets_joined()
    for k,v in gamification.rewards.Badges.JOIN_DATASET.value.items():
        if k <= joined_datasets:
            if not user.has_badge(v.reason):
                badges.append(v)

    user.add_rewards(rewards=[], badges=badges)

    return responses.response(True, badges=badges)

@bp.route('/leave', methods=['POST'])
@jwt_required()
def leave_dataset():
    '''Leave a dataset by its ID.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    dataset_id = data['dataset_id']

    dataset = db.admin.Dataset(dataset_id)

    if dataset.is_special:
        return responses.response(False, message=_('This is a special dataset and cannot be left.'))
    
    if dataset.remove_participant(user):
        return responses.response(True)
    else:
        return responses.response(False, message=_('You cannot leave this dataset, as you are an owner and it has data associated with it.'))


@bp.route('/is-owner/<dataset_id>', methods=['GET'])
@jwt_required()
def is_owner(dataset_id):
    '''Check if the user is an owner of a dataset.'''
    user = db.admin.User(get_jwt_identity())
    dataset = db.admin.Dataset(dataset_id)

    result = dataset.has_owner(user)

    return responses.response(True, is_owner=result)

@bp.route('/set-owner', methods=['POST'])
@jwt_required()
def set_owner():
    '''Set a user as an owner of a dataset.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    dataset = db.admin.Dataset(data['dataset_id'])
    owner = db.admin.User(data['username'])
    value = data['value']

    if not dataset.has_owner(user):
        return responses.response(False, message=_('You are not an owner of this dataset.'))

    if user == owner:
        return responses.response(False, message=_('You cannot set yourself as an owner of this dataset.'))

    dataset.set_owner_status(owner, value)

    return responses.response(True)


@bp.route('/members/<dataset_id>', methods=['GET'])
@jwt_required()
def get_members(dataset_id):
    '''Get the members of a dataset.'''
    user = db.admin.User(get_jwt_identity())
    dataset = db.admin.Dataset(dataset_id)

    if not dataset.has_owner(user):
        return responses.response(False, message=_('You are not an owner of this dataset.'))

    members = dataset.get_members()

    return responses.response(True, members=members)

@bp.route('/<dataset_id>/str', methods=['GET'])
@jwt_required()
def get_dataset_str(dataset_id):
    '''Get a dataset by ID.'''
    
    user = db.admin.User(get_jwt_identity())
    dataset = db.admin.Dataset(dataset_id)

    if not dataset.has_participant(user):
        return responses.response(False, message=_('You do not have access to this dataset.'))

    result = dataset.dataset_str

    return responses.response(True, data=result)
