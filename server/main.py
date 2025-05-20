from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import os
from datetime import timedelta
import json

import llm
import db_admi as db_admin
import db_users
from sql_code import SQLException

from sql_code import QueryResult

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
CORS(app)

jwt = JWTManager(app)

def response(success: bool = True, **kwargs):
    return {
        'success': success,
        **kwargs
    }

def response_query(*results: QueryResult, is_builtin: bool = False) -> Response:
    return jsonify([
        {
            'success': query.success,
            'builtin': is_builtin,
            'query': query.query,
            'type': query.type,
            'data': query.result,
            'id': query.id,
        }
        for query in results
    ])

OK = response()
NOT_IMPLEMENTED = 'This feature is not implemented yet. Please check back later.'

#################### Generic ####################
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if not db_admin.can_login(username, password):
        return response(False, message='Cannot login. Please check your username and password.')
    
    access_token = create_access_token(identity=username, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(identity=username, expires_delta=timedelta(days=7))

    return response(True, access_token=access_token, refresh_token=refresh_token)

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user, expires_delta=timedelta(minutes=15))

    return response(True, access_token=access_token)

from flask import Response

import time

@app.route('/run-query', methods=['POST'])
@jwt_required()
def run_query():
    username = get_jwt_identity()
    data = request.get_json()
    query = data['query']
    exercise_id = int(data['exercise_id'])

    batch_id = db_admin.log_query_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    def generate_results():
        for query_result in db_users.execute_queries(username=username, query_str=query):
            query_id = db_admin.log_query(
                batch_id=batch_id,
                query=query_result.query,
                success=query_result.success,
                result_str=str(query_result) if isinstance(query_result, SQLException) else query_result.result
            )
            query_result.id = query_id

            yield json.dumps({
                'success': query_result.success,
                'builtin': False,
                'query': query_result.query,
                'type': query_result.type,
                'data': query_result.result,
                'id': query_id,
                'notices': query_result.notices,
            }) + '\n'  # Important: one JSON object per line

    return Response(generate_results(), content_type='application/x-ndjson')


@app.route('/message-feedback', methods=['POST'])
@jwt_required()
def feedback():
    username = get_jwt_identity()
    data = request.get_json()
    message_id = data['message_id']
    feedback = data['feedback']

    db_admin.log_feedback(
        message_id=message_id,
        feedback=feedback,
        username=username,
    )

    return OK

@app.route('/create-dataset', methods=['POST'])
@jwt_required()
def create_dataset():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    dataset = db_admin.get_exercise_dataset(
        exercise_id=exercise_id
    )

    def generate_results():
        for query_result in db_users.execute_queries(username=username, query_str=dataset):
            yield json.dumps({
                'success': query_result.success,
                'builtin': True,
                'query': query_result.query,
                'type': query_result.type,
                'data': query_result.result,
                'id': None,
            }) + '\n'  # Important: one JSON object per line

    return Response(generate_results(), content_type='application/x-ndjson')

@app.route('/get-datasets', methods=['GET'])
@jwt_required()
def get_datasets():
    username = get_jwt_identity()

    datasets = db_admin.get_datasets(username)

    return response(True, data=datasets)

@app.route('/get-dataset', methods=['GET'])
@jwt_required()
def get_dataset():
    username = get_jwt_identity()
    data = request.args
    dataset_id = data.get('id')
    if dataset_id == '':
        dataset_id = None

    result = db_admin.get_dataset(dataset_id)

    return response(True, data=result)

#################### Assignments ####################
@app.route('/get-assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    username = get_jwt_identity()

    assignments = db_admin.get_assignments(username)

    return response(True, data=assignments)

@app.route('/get-assignment-students', methods=['POST'])
@jwt_required()
def get_assignment_students():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    students = db_admin.get_assignment_students(username, exercise_id)

    return response(True, students=students)

@app.route('/get-all-exercises', methods=['GET'])
@jwt_required()
def get_all_exercises():
    username = get_jwt_identity()

    exercises = db_admin.get_all_exercises()

    return response(True, data=exercises)

@app.route('/get-exercise', methods=['GET'])
@jwt_required()
def get_exercise():
    username = get_jwt_identity()
    data = request.args
    exercise_id = data.get('id')

    result = db_admin.get_exercise(exercise_id, username)

    return response(True, data=result)

@app.route('/submit-assignment', methods=['POST'])
@jwt_required()
def submit_exercise():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    db_admin.submit_assignment(username, exercise_id)

    return OK

@app.route('/unsubmit-assignment', methods=['POST'])
@jwt_required()
def unsubmit_exercise():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    db_admin.unsubmit_assignment(username, exercise_id)

    return OK

#################### Exercises Management ####################

@app.route('/add-exercise', methods=['POST'])
@jwt_required()
def add_exercise():
    username = get_jwt_identity()
    data = request.get_json()
    title = data['title']
    request_text = data['request']
    dataset_id = data['dataset_id']
    expected_answer = data['expected_answer']

    db_admin.add_exercise(
        title=title,
        request=request_text,
        dataset_id=dataset_id,
        expected_answer=expected_answer
    )

    return OK

@app.route('/edit-exercise', methods=['POST'])
@jwt_required()
def edit_exercise():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']
    title = data['title']
    request_text = data['request']
    dataset_id = data['dataset_id']
    if dataset_id == '':
        dataset_id = None
    expected_answer = data['expected_answer']

    db_admin.edit_exercise(
        exercise_id=exercise_id,
        title=title,
        request=request_text,
        dataset_id=dataset_id,
        expected_answer=expected_answer
    )

    return OK

@app.route('/delete-exercise', methods=['POST'])
@jwt_required()
def delete_exercise():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']

    db_admin.delete_exercise(
        exercise_id=exercise_id
    )

    return OK

@app.route('/assign-exercise', methods=['POST'])
@jwt_required()
def assign_exercise():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = data['exercise_id']
    student_id = data['student_id']
    value = data['value']

    if value:
        db_admin.assign_exercise(
            teacher=username,
            exercise_id=exercise_id,
            student=student_id
        )
    else:
        db_admin.unassign_exercise(
            exercise_id=exercise_id,
            student=student_id
        )

    return OK


#################### User data ####################
@app.route('/me', methods=['GET'])
@jwt_required()
def me():
    username = get_jwt_identity()

    result = db_admin.get_user_info(username)
    if result is None:
        return response(False)
    
    return response(True, **result)

#################### Builtin ####################
@app.route('/show-search-path', methods=['POST'])
@jwt_required()
def show_search_path():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db_users.show_search_path(username)

    batch_id = db_admin.log_query_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_id = db_admin.log_query(
        batch_id=batch_id,
        query=result.query,
        success=result.success,
        result_str=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

@app.route('/list-schemas', methods=['POST'])
@jwt_required()
def list_schemas():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db_users.list_schemas(username)

    batch_id = db_admin.log_query_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_id = db_admin.log_query(
        batch_id=batch_id,
        query=result.query,
        success=result.success,
        result_str=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

@app.route('/list-tables', methods=['POST'])
@jwt_required()
def list_tables():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db_users.list_tables(username)

    batch_id = db_admin.log_query_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_id = db_admin.log_query(
        batch_id=batch_id,
        query=result.query,
        success=result.success,
        result_str=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

@app.route('/list-all-tables', methods=['POST'])
@jwt_required()
def list_all_tables():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db_users.list_all_tables(username)

    batch_id = db_admin.log_query_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_id = db_admin.log_query(
        batch_id=batch_id,
        query=result.query,
        success=result.success,
        result_str=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

@app.route('/list-constraints', methods=['POST'])
@jwt_required()
def list_constraints():
    username = get_jwt_identity()
    data = request.get_json()
    exercise_id = int(data['exercise_id'])
    
    result = db_users.list_constraints(username)

    batch_id = db_admin.log_query_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_id = db_admin.log_query(
        batch_id=batch_id,
        query=result.query,
        success=result.success,
        result_str=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

#################### Syntax Error ####################
@app.route('/explain-error-message', methods=['POST'])
@jwt_required()
def explain_error_message():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']
    
    query = db_admin.get_query(query_id)
    exception = db_admin.get_query_result(query_id)
    answer = llm.explain_error_message(query, exception)

    answer_id = db_admin.log_message(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return response(answer=answer, id=answer_id)

@app.route('/locate-error-cause', methods=['POST'])
@jwt_required()
def locate_error_cause():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db_admin.get_query(query_id)
    exception = db_admin.get_query_result(query_id)
    answer = llm.locate_error_cause(query, exception)

    answer_id = db_admin.log_message(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return response(answer=answer, id=answer_id)

@app.route('/provide-error-example', methods=['POST'])
@jwt_required()
def provide_error_example():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db_admin.get_query(query_id)
    exception = db_admin.get_query_result(query_id)
    # answer = llm.provide_error_example(query, exception)
    answer = NOT_IMPLEMENTED
    
    answer_id = db_admin.log_message(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return response(answer=answer, id=answer_id)

@app.route('/fix-query', methods=['POST'])
@jwt_required()
def fix_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db_admin.get_query(query_id)
    exception = db_admin.get_query_result(query_id)
    answer = llm.fix_query(query, exception)

    answer_id = db_admin.log_message(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return response(answer=answer, id=answer_id)

#################### Syntax OK ####################
@app.route('/describe-my-query', methods=['POST'])
@jwt_required()
def describe_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db_admin.get_query(query_id)
    answer = llm.describe_my_query(query)

    answer_id = db_admin.log_message(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return response(answer=answer, id=answer_id)

@app.route('/explain-my-query', methods=['POST'])
@jwt_required()
def explain_my_query():
    username = get_jwt_identity()
    data = request.get_json()
    query_id = data['query_id']
    msg_idx = data['msg_idx']

    query = db_admin.get_query(query_id)
    answer = llm.explain_my_query(query)

    answer_id = db_admin.log_message(
        answer=answer,
        button=request.path,
        query_id=query_id,
        msg_idx=msg_idx
    )

    return response(answer=answer, id=answer_id)


###################### Main #####################

if __name__ == '__main__':
    db_users.start_cleanup_thread()
    
    app.run(
    	host='0.0.0.0',
    	debug=True
    )

