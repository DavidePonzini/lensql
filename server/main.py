from flask import Flask, request
from flask_cors import CORS
import json

import llm
import db_admin as db_admin
import db_users

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

    return response(True, token={
        'username': username,
        })
    

@app.route('/run-query', methods=['POST'])
def run_query():
    data = request.get_json()
    username = data['username']
    query = data['query']

    query_results = db_users.execute_queries(
        username=username,
        query_str=query
    )

    for query_result in query_results:
        query_id = db_admin.log_query(
            username=username,
            query=query_result.query,
            success=query_result.success
            # type=query_result.type,
            # result=query_result.result,
        )

        query_result.id = query_id

    return response_query(*query_results)

@app.route('/message-feedback', methods=['POST'])
def feedback():
    data = request.get_json()
    msg_id = data['msg_id']
    feedback = data['feedback']

    db_admin.log_feedback(
        message_id=msg_id,
        feedback=feedback
    )

    return OK

#################### Builtin ####################
@app.route('/list-schemas', methods=['POST'])
def list_schemas():
    data = request.get_json()
    username = data['username']
    
    result = db_users.list_schemas(username)

    query_id = db_admin.log_query(
        username=username,
        query=result.query,
        success=result.success
        # type=result.type,
        # result=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

@app.route('/list-tables', methods=['POST'])
def list_tables():
    data = request.get_json()
    username = data['username']
    
    result = db_users.list_tables(username)

    query_id = db_admin.log_query(
        username=username,
        query=result.query,
        success=result.success
        # type=result.type,
        # result=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

@app.route('/list-constraints', methods=['POST'])
def list_constraints():
    data = request.get_json()
    username = data['username']
    
    result = db_users.list_constraints(username)

    query_id = db_admin.log_query(
        username=username,
        query=result.query,
        success=result.success
        # type=result.type,
        # result=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)


@app.route('/show-search-path', methods=['POST'])
def show_search_path():
    data = request.get_json()
    username = data['username']
    
    result = db_users.show_search_path(username)

    query_id = db_admin.log_query(
        username=username,
        query=result.query,
        success=result.success
        # type=result.type,
        # result=result.result
    )

    result.id = query_id

    return response_query(result, is_builtin=True)

#################### Syntax Error ####################
@app.route('/explain-error-message', methods=['POST'])
def explain_error_message():
    data = request.get_json()
    query_id = data['query_id']
    exception = data['exception']
    chat_id = data['chat_id']
    msg_id = data['msg_id']
    
    query = db_admin.get_query(query_id)
    answer = llm.explain_error_message(query, exception)

    answer_id = db_admin.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer, id=answer_id)

@app.route('/locate-error-cause', methods=['POST'])
def locate_error_cause():
    data = request.get_json()
    query_id = data['query_id']
    exception = data['exception']
    chat_id = data['chat_id']
    msg_id = data['msg_id']

    query = db_admin.get_query(query_id)
    answer = llm.locate_error_cause(query, exception)

    answer_id = db_admin.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer, id=answer_id)

@app.route('/provide-error-example', methods=['POST'])
def provide_error_example():
    data = request.get_json()
    query_id = data['query_id']
    exception = data['exception']
    chat_id = data['chat_id']
    msg_id = data['msg_id']

    query = db_admin.get_query(query_id)
    # answer = llm.provide_error_example(query, exception)
    answer = NOT_IMPLEMENTED
    
    answer_id = db_admin.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer, id=answer_id)

@app.route('/fix-query', methods=['POST'])
def fix_query():
    data = request.get_json()
    query_id = data['query_id']
    exception = data['exception']
    chat_id = data['chat_id']
    msg_id = data['msg_id']

    query = db_admin.get_query(query_id)
    answer = llm.fix_query(query, exception)

    answer_id = db_admin.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer, id=answer_id)

#################### Syntax OK ####################
@app.route('/describe-my-query', methods=['POST'])
def describe_my_query():
    data = request.get_json()
    query_id = data['query_id']
    chat_id = data['chat_id']
    msg_id = data['msg_id']

    query = db_admin.get_query(query_id)
    answer = llm.describe_my_query(query)

    answer_id = db_admin.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=None,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer, id=answer_id)

@app.route('/explain-my-query', methods=['POST'])
def explain_my_query():
    data = request.get_json()
    query_id = data['query_id']
    chat_id = data['chat_id']
    msg_id = data['msg_id']

    query = db_admin.get_query(query_id)
    answer = llm.explain_my_query(query)

    answer_id = db_admin.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=None,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer, id=answer_id)


###################### Main #####################

if __name__ == '__main__':
    db_users.start_cleanup_thread()
    
    app.run(
    	host='0.0.0.0',
    	debug=True
    )

