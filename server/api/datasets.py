'''This module handles dataset-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .util import responses
from server import db


bp = Blueprint('datasets', __name__)

@bp.route('/', methods=['GET'])
@jwt_required()
def get_dataset():
    '''Get a dataset by ID.'''
    
    username = get_jwt_identity()
    data = request.args
    class_id = data['class_id']

    if db.admin.classes.has_participant(class_id=class_id, username=username) is False:
        return responses.response(False, message='You do not have access to this dataset.')
    
    result = db.admin.classes.get_dataset(class_id)

    return responses.response(True, data=result)
