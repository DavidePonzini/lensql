'''This module handles authentication-related endpoints for the API.'''

from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta
from flask_babel import _

from server import db
from .util import responses

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    '''Login endpoint to authenticate users and return JWT tokens.'''
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = db.admin.User(username)

    if not user.can_login(password):
        return responses.response(False, message=_('Cannot login. Please check your username and password.'))

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
def register():
    '''Register a new user and return JWT tokens.'''
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']
    school = data['school']

    user = db.admin.User(username)

    if user.exists():
        return responses.response(False, message=_('Username already exists. Please choose a different username.'))
    
    default_datasets = [
        db.admin.Dataset('_EXPLORE'),
        db.admin.Dataset('_WELCOME_MIEDEMA'),
    ]

    if not db.register_user(user, password, email=email, school=school, datasets=default_datasets):
        return responses.response(False, message=_('Registration failed. Please try again.'))

    return responses.response(True)

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def reset_password():
    '''Reset the password for the current user.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    new_password = data['new_password']

    if not user.change_password(new_password):
        return responses.response(False, message=_('Failed to reset password. Please try again.'))

    return responses.response(True, message=_('Password reset successfully.'))