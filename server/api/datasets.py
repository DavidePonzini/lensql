'''This module handles dataset-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .util import responses
from server import db


bp = Blueprint('dataset', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_dataset():
    '''Get a dataset by ID.'''
    
    username = get_jwt_identity()
    data = request.args
    dataset_name = data.get('name') or None

    result = db.admin.dataset.get(dataset_name)

    return responses.response(True, data=result)

@bp.route('/list', methods=['GET'])
@jwt_required()
def list_datasets():
    '''List all datasets available to the user.'''

    username = get_jwt_identity()

    datasets = db.admin.dataset.list_all(username)

    return responses.response(True, data=datasets)

