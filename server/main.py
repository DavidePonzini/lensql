from flask import Flask, request
from flask_cors import CORS
import json

import llm
import db_admi as db_admin
import db_users
from sql_code import SQLException

from sql_code import QueryResult
from dav_tools import messages

app = Flask(__name__)
CORS(app)


def response(success: bool = True, **kwargs):
    return {
        'success': success,
        **kwargs
    }

def response_query(*results: QueryResult, is_builtin: bool = False) -> str:
    return json.dumps([
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

    return response(True, token=username)

@app.route('/get-assignments', methods=['GET'])
def get_assignments():
    data = request.args
    username = data.get('username')

    assignments = db_admin.get_assignments(username)

    return response(True, data=assignments)

@app.route('/get-exercise', methods=['GET'])
def get_exercise():
    data = request.args
    assignment_id = data.get('id')

    result = db_admin.get_exercise(assignment_id)

    return response(True, data=result)


@app.route('/run-query', methods=['POST'])
def run_query():
    data = request.get_json()
    username = data['username']
    query = data['query']
    exercise_id = int(data['exercise_id'])

    batch_id = db_admin.log_query_batch(
        username=username,
        exercise_id=exercise_id if exercise_id > 0 else None
    )

    query_results = db_users.execute_queries(
        username=username,
        query_str=query
    )

    for query_result in query_results:
        query_id = db_admin.log_query(
            batch_id=batch_id,
            query=query_result.query,
            success=query_result.success,
            result_str=str(query_result) if isinstance(query_result, SQLException) else query_result.result
        )

        query_result.id = query_id

    return response_query(*query_results)

@app.route('/message-feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    message_id = data['message_id']
    feedback = data['feedback']

    db_admin.log_feedback(
        message_id=message_id,
        feedback=feedback
    )

    return OK

#################### Builtin ####################
@app.route('/show-search-path', methods=['POST'])
def show_search_path():
    data = request.get_json()
    username = data['username']
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
def list_schemas():
    data = request.get_json()
    username = data['username']
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
def list_tables():
    data = request.get_json()
    username = data['username']
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

@app.route('/list-constraints', methods=['POST'])
def list_constraints():
    data = request.get_json()
    username = data['username']
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
def explain_error_message():
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
def locate_error_cause():
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
def provide_error_example():
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
def fix_query():
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
def describe_my_query():
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
def explain_my_query():
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

