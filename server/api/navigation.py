'''This module handles dataset-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import _

from server import db
from .util import responses

bp = Blueprint('navigation', __name__)


@bp.route('/log', methods=['POST'])
@jwt_required()
def log_navigation():
    '''Log a navigation event.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    url = data['url']
    event = data['event']

    user.log_navigation(url, event)

    return responses.response(True)