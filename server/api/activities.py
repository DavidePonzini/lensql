'''This module handles activity-related endpoints for the API.'''

import json
import re
from psycopg2.errors import UniqueViolation
from dataclasses import asdict
from datetime import datetime, timezone

from flask import Blueprint, current_app, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_babel import _
from sqlscope import Dialect

from server import db, gamification
from .util import responses

bp = Blueprint('activities', __name__)


@bp.route('/rename-id', methods=['POST'])
@jwt_required()
def rename_activity_id():
    '''Allow administrators to rename any activity, regardless of membership.'''
    user = db.admin.User(get_jwt_identity())
    if not user.is_admin:
        return responses.response(False, message=_('You do not have permission to perform this action.'))

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return responses.response(False, message=_('Invalid activity ID.'))
    activity_id = data.get('activity_id')
    new_id = data.get('new_activity_id')
    if not isinstance(activity_id, str) or not activity_id.strip() or not isinstance(new_id, str):
        return responses.response(False, message=_('Invalid activity ID.'))
    new_id = new_id.strip().upper()
    if not re.fullmatch(r'[A-Z0-9_-]+', new_id):
        return responses.response(False, message=_('Activity IDs may contain only letters, numbers, underscores and hyphens.'))

    activity = db.admin.Activity(activity_id.strip())
    try:
        if not activity.rename_id(new_id):
            return responses.response(False, message=_('Activity does not exist.'))
    except UniqueViolation:
        return responses.response(False, message=_('This activity ID is already in use.'))
    return responses.response(True, activity_id=new_id)


def _parse_activity_timestamp(value: str | None, field_name: str) -> datetime | None:
    '''Parse an optional ISO-8601 timestamp supplied by the activity form.'''

    if not value:
        return None

    try:
        timestamp = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)
    except (AttributeError, ValueError) as error:
        raise ValueError(_('%(field)s must be a valid date and time.', field=field_name)) from error


def _activity_timestamps(data: dict) -> tuple[datetime | None, datetime | None]:
    start = _parse_activity_timestamp(data.get('activity_start_ts'), _('Activity start'))
    end = _parse_activity_timestamp(data.get('activity_end_ts'), _('Activity end'))
    if start and end and start > end:
        raise ValueError(_('Activity start must be before activity end.'))
    return start, end


def _format_activity_import_error(error: Exception) -> str:
    '''Format activity import errors into user-facing messages with context.'''

    if isinstance(error, json.JSONDecodeError):
        return _(
            'Failed to import activity. JSON syntax error at line %(line)s, column %(column)s: %(details)s.',
            line=error.lineno,
            column=error.colno,
            details=error.msg,
        )

    if isinstance(error, KeyError):
        field = error.args[0] if error.args else 'unknown'
        return _(
            'Failed to import activity. Missing required field: %(field)s.',
            field=field,
        )

    if isinstance(error, (TypeError, ValueError)):
        details = str(error).strip() or _('Invalid activity content.')
        return _(
            'Failed to import activity. %(details)s',
            details=details,
        )

    return _('Failed to import activity because the server encountered an error.')


class ActivitiesAPI(MethodView):
    decorators = [jwt_required()]

    def get(self):
        '''List activities visible to the user.'''

        user = db.admin.User(get_jwt_identity())

        result = user.list_activities()

        return responses.response(True, data=result)

    def post(self):
        '''Create a new activity.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        title = data['title']
        description = data['description']
        activity_str = data['activity']
        activity_search_path = data['search_path'] or 'public'   # Handle empty string
        dbms = Dialect(data['dbms'])
        try:
            activity_start_ts, activity_end_ts = _activity_timestamps(data) if user.is_teacher else (None, None)
        except ValueError as error:
            return responses.response(False, message=str(error))

        activity = db.admin.Activity.create(
            title=title,
            description=description,
            activity_str=activity_str,
            dbms=dbms,
            search_path=activity_search_path,
            activity_start_ts=activity_start_ts,
            activity_end_ts=activity_end_ts,
        )
        activity.add_participant(user)
        activity.set_owner_status(user, True)

        return responses.response(True)

    def put(self):
        '''Rename a activity.'''

        user = db.admin.User(get_jwt_identity())

        data = request.get_json()
        activity_id = data['activity_id']
        title = data['title']
        description = data['description']
        activity_str = data['activity']
        activity_search_path = data['search_path'] or 'public'   # Handle empty string
        dbms = Dialect(data['dbms'])

        activity = db.admin.Activity(activity_id)
        if not activity.has_owner(user):
            return responses.response(False, message=_('You are not authorized to modify this activity.'))

        if not user.is_teacher and ('activity_start_ts' in data or 'activity_end_ts' in data):
            return responses.response(False, message=_('Only teachers can modify activity dates.'))

        try:
            activity_start_ts, activity_end_ts = _activity_timestamps(data)
        except ValueError as error:
            return responses.response(False, message=str(error))

        activity.update(
            title=title,
            description=description,
            activity_str=activity_str,
            search_path=activity_search_path,
            dbms=dbms,
            activity_start_ts=activity_start_ts,
            activity_end_ts=activity_end_ts,
        )

        return responses.response(True)

# Register all methods (GET, POST, PUT, DELETE) on /
#   Note: trailing slash causes nginx to redirect, leading to CORS error
bp.add_url_rule('', view_func=ActivitiesAPI.as_view('activities_api'))

@bp.route('/get/<activity_id>', methods=['GET'])
@jwt_required()
def get_activity(activity_id):
    '''Get a activity by its ID.'''
    user = db.admin.User(get_jwt_identity())

    activity = db.admin.Activity(activity_id)

    if not activity.exists():
        return responses.response(False, message='Activity does not exist.')
    if not activity.has_participant(user):
        return responses.response(False, message=_('You do not have access to this activity.'))

    result = {
        'title': activity.name,
        'description': activity.description,
        'activity_str': activity.activity_str,
        'search_path': activity.search_path,
        'dbms': activity.dbms.value,
    }

    if user.is_teacher:
        result.update({
            'activity_start_ts': activity.activity_start_ts.isoformat() if activity.activity_start_ts else None,
            'activity_end_ts': activity.activity_end_ts.isoformat() if activity.activity_end_ts else None,
        })

    return responses.response(True, data=result)

@bp.route('/join', methods=['POST'])
@jwt_required()
def join_activity():
    '''Join a activity by its ID.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    activity_id = str(data['activity_id']).strip().upper()    # sanitize join code

    activity = db.admin.Activity(activity_id)

    if not activity.exists():
        return responses.response(False, message=_('Activity does not exist.'))
    activity.add_participant(user)

    badges = []

    joined_activities = user.count_all_activities_joined()
    for k,v in gamification.rewards.Badges.JOIN_ACTIVITY.value.items():
        if k <= joined_activities:
            if not user.has_badge(v.reason):
                badges.append(v)

    user.add_rewards(rewards=[], badges=badges)

    return responses.response(True, badges=badges)

@bp.route('/leave', methods=['POST'])
@jwt_required()
def leave_activity():
    '''Leave a activity by its ID.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    activity_id = data['activity_id']

    activity = db.admin.Activity(activity_id)

    if activity.is_special:
        return responses.response(False, message=_('This is a special activity and cannot be left.'))

    if activity.remove_participant(user):
        return responses.response(True)
    else:
        return responses.response(False, message=_('You cannot leave this activity, as you are an owner and it has data associated with it.'))


@bp.route('/is-owner/<activity_id>', methods=['GET'])
@jwt_required()
def is_owner(activity_id):
    '''Check if the user is an owner of a activity.'''
    user = db.admin.User(get_jwt_identity())
    activity = db.admin.Activity(activity_id)

    result = activity.has_owner(user)

    return responses.response(True, is_owner=result)

@bp.route('/set-owner', methods=['POST'])
@jwt_required()
def set_owner():
    '''Set a user as an owner of a activity.'''
    user = db.admin.User(get_jwt_identity())

    data = request.get_json()
    activity = db.admin.Activity(data['activity_id'])
    owner = db.admin.User(data['username'])
    value = data['value']

    if not activity.has_owner(user):
        return responses.response(False, message=_('You are not an owner of this activity.'))

    if user == owner:
        return responses.response(False, message=_('You cannot set yourself as an owner of this activity.'))

    activity.set_owner_status(owner, value)

    return responses.response(True)


@bp.route('/add-user', methods=['POST'])
@jwt_required()
def add_user_to_activity():
    '''Admin endpoint to add a user to a activity with optional owner status.'''
    admin_user = db.admin.User(get_jwt_identity())

    if not admin_user.is_admin:
        return responses.response(False, message=_('You do not have permission to perform this action.'))

    data = request.get_json()
    activity_id = data['activity_id']
    username = data['username']
    is_owner = data.get('is_owner', False)

    activity = db.admin.Activity(activity_id)
    target_user = db.admin.User(username)

    if not activity.exists():
        return responses.response(False, message=_('Activity does not exist.'))

    if not target_user.exists():
        return responses.response(False, message=_('User does not exist.'))

    activity.add_participant(target_user)
    activity.set_owner_status(target_user, is_owner)

    return responses.response(True)


@bp.route('/members/<activity_id>', methods=['GET'])
@jwt_required()
def get_members(activity_id):
    '''Get the members of a activity.'''
    user = db.admin.User(get_jwt_identity())
    activity = db.admin.Activity(activity_id)

    if not activity.has_owner(user):
        return responses.response(False, message=_('You are not an owner of this activity.'))

    members = activity.get_members()

    return responses.response(True, members=members)

@bp.route('/<activity_id>/str', methods=['GET'])
@jwt_required()
def get_activity_str(activity_id):
    '''Get a activity by ID.'''

    user = db.admin.User(get_jwt_identity())
    activity = db.admin.Activity(activity_id)

    if not activity.has_participant(user):
        return responses.response(False, message=_('You do not have access to this activity.'))

    result = activity.activity_str

    return responses.response(True, data=result)


@bp.route('/export/<activity_id>', methods=['GET'])
@jwt_required()
def export_activity(activity_id):
    '''Export a activity by ID.'''

    user = db.admin.User(get_jwt_identity())
    activity = db.admin.Activity(activity_id)

    if not activity.has_owner(user):
        return responses.response(False, message=_('You are not an owner of this activity.'))

    return responses.response(True, data=asdict(activity.dump()))


@bp.route('/import', methods=['POST'])
@jwt_required()
def import_activity():
    '''Import a activity from an exported JSON payload.'''

    user = db.admin.User(get_jwt_identity())
    data = request.get_json()
    payload = data['payload']

    try:
        activity = db.admin.Activity.load_json(payload)
        activity.add_participant(user)
        activity.set_owner_status(user, True)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        return responses.response(False, message=_format_activity_import_error(error))
    except Exception:
        current_app.logger.exception('Activity import failed.')
        return responses.response(
            False,
            message=_('Failed to import activity because the server encountered an error.'),
        )

    return responses.response(True, activity_id=activity.activity_id)


@bp.route('/generation-options', methods=['GET'])
@jwt_required()
def generation_options():
    from sqlexercise.error_requirements import ERROR_REQUIREMENTS_MAP
    from sqlerrors import SqlErrorCategory, SqlErrors
    user = db.admin.User(get_jwt_identity())
    errors = [
        {'id': error.value, 'name': error.definition.name,
         'category': error.definition.category.value, 'supported': error in ERROR_REQUIREMENTS_MAP}
        for error in sorted(SqlErrors, key=lambda error: error.value) if not error.definition.is_deprecated
    ]
    activities = [activity for activity in user.list_activities() if activity['is_owner']]
    categories = [{'id': category.value} for category in SqlErrorCategory]
    return responses.response(True, errors=errors, categories=categories, activities=activities,
                              ai_generation_credits=user.ai_generation_credits)


@bp.route('/generation-students', methods=['POST'])
@jwt_required()
def generation_students():
    user = db.admin.User(get_jwt_identity())
    data = request.get_json(silent=True)
    ids = data.get('activity_ids') if isinstance(data, dict) else None
    if not isinstance(ids, list) or not ids or any(not isinstance(i, str) or not i for i in ids):
        return responses.response(False, message=_('Select at least one activity.'))
    from dav_tools import database
    from server.db.admin.connection import db as admin_db, SCHEMA
    # Validate every selected activity before returning any students.
    for activity_id in set(ids):
        if not db.admin.Activity(activity_id).has_owner(user):
            return responses.response(False, message=_('You are not a teacher in all selected activities.'))
    query = database.sql.SQL('''
        SELECT DISTINCT username FROM {schema}.activity_members
        WHERE activity_id = ANY(%(ids)s) AND is_active = TRUE AND is_owner = FALSE
        ORDER BY username
    ''').format(schema=database.sql.Identifier(SCHEMA))
    students = [row[0] for row in admin_db.execute_and_fetch(query, {'ids': ids})]
    return responses.response(True, students=students)


@bp.route('/generate', methods=['POST'])
@jwt_required()
def generate():
    from sqlerrors import SqlErrors
    from sqlexercise import DifficultyLevel
    from sqlexercise.error_requirements import ERROR_REQUIREMENTS_MAP
    from server.generation import generate_activity
    user = db.admin.User(get_jwt_identity())
    data = request.get_json(silent=True)
    try:
        if not isinstance(data, dict):
            raise ValueError()
        title = data.get('title', '').strip()
        prefix = data.get('prefix', 'Exercise ')
        selections = data.get('errors')
        dataset_str = data.get('dataset_str')
        search_path = data.get('search_path', 'public')
        if dataset_str is not None:
            if not isinstance(dataset_str, str) or len(dataset_str.encode('utf-8')) > 2_000_000:
                raise ValueError()
            dataset_str = dataset_str.strip() or None
        if dataset_str:
            if not isinstance(search_path, str) or not search_path.strip() or len(search_path) > 255:
                raise ValueError()
            search_path = search_path.strip()
        else:
            search_path = 'public'
        if not title or len(title) > 255 or not isinstance(prefix, str) or len(prefix) > 240:
            raise ValueError()
        if not isinstance(selections, list) or not selections:
            raise ValueError()
        errors = []
        for selection in selections:
            if not isinstance(selection, dict):
                raise ValueError()
            error_id, count = selection.get('error_id'), selection.get('count')
            difficulty = selection.get('difficulty', 1)
            if any(type(v) is not int for v in (error_id, count, difficulty)) or not 1 <= count <= 100:
                raise ValueError()
            error = SqlErrors(error_id)
            if error not in ERROR_REQUIREMENTS_MAP or error.definition.is_deprecated:
                raise ValueError()
            errors.extend([(error, DifficultyLevel(difficulty))] * count)
            if len(errors) > 100:
                raise ValueError()
    except (ValueError, TypeError, AttributeError):
        return responses.response(False, message=_('Select valid errors and counts (maximum 100 exercises), a title and a prefix.'))
    if dataset_str:
        from sqlexercise.assignments import Dataset
        from server.generation.dataset import generation_dataset_sql
        try:
            Dataset.from_sql(generation_dataset_sql(dataset_str), sql_dialect='postgres')
        except Exception:
            return responses.response(False, message=_('Provide valid PostgreSQL dataset SQL with CREATE TABLE statements.'))
    if not user.reserve_generation_credits(len(errors) + 1):
        return responses.response(False, message=_('Insufficient generation credits.'))
    language = 'it' if request.headers.get('X-Language', '').startswith('it') else 'en'
    failure_message = _('Generation failed. Exercise credits have been refunded; the 1-credit generation fee was charged.')

    def run_generation(on_progress=None):
        generated_count = len(errors)

        def progress(event):
            nonlocal generated_count
            if event['stage'] == 'saving':
                generated_count = event['completed']
            if on_progress:
                on_progress(event)

        try:
            activity_id = generate_activity(user, errors, title=title, prefix=prefix,
                                            dataset_str=dataset_str, search_path=search_path,
                                            language=language, on_progress=progress)
        except Exception:
            user.refund_generation_credits(len(errors))
            current_app.logger.exception('Activity generation failed.')
            return dict(success=False, message=failure_message)
        failed_count = len(errors) - generated_count
        if failed_count:
            user.refund_generation_credits(failed_count)
        return dict(success=True, activity_id=activity_id,
                    generated_count=generated_count, failed_count=failed_count,
                    ai_generation_credits=user.ai_generation_credits)

    if data.get('stream') is not True:
        return responses.response(**run_generation())

    from queue import Queue, Empty
    from threading import Thread
    from flask import Response
    app = current_app._get_current_object()
    events = Queue()

    def worker():
        # Finish saving or refunding even if the browser disconnects.
        with app.app_context():
            events.put(dict(type='result', **run_generation(
                lambda event: events.put(dict(type='progress', **event)))))

    Thread(target=worker, daemon=True).start()

    def stream():
        while True:
            try:
                event = events.get(timeout=15)
            except Empty:
                yield '\n'
                continue
            yield json.dumps(event) + '\n'
            if event['type'] == 'result':
                break

    return Response(stream(), content_type='application/x-ndjson',
                    headers={'X-Accel-Buffering': 'no', 'Cache-Control': 'no-cache'})
