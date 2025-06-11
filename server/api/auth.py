'''This module handles authentication-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta

from server import db
from .util import responses

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    '''Login endpoint to authenticate users and return JWT tokens.'''
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not db.admin.auth.can_login(username, password):
        return responses.response(False, message='Cannot login. Please check your username and password.')
    
    access_token = create_access_token(identity=username, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(identity=username, expires_delta=timedelta(days=7))

    return responses.response(True, access_token=access_token, refresh_token=refresh_token)

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    '''Refresh the access token using the refresh token.'''
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=15))

    return responses.response(True, access_token=access_token)

@bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    '''Register a new user and return JWT tokens.'''
    if not db.admin.users.is_admin(get_jwt_identity()):
        return responses.response(False, message='Only admins can register new users.')

    data = request.get_json()
    username = data['username']
    password = data['password']
    is_teacher = data['is_teacher']
    is_admin = data['is_admin']

    if not db.register_user(username, password, is_teacher=is_teacher, is_admin=is_admin):
        return responses.response(False, message='Registration failed. Please try again.')
    
    return responses.response(True)
