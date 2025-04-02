import os
from flask import Flask, request
from flask_cors import CORS
import json

import llm
import db


app = Flask(__name__)
CORS(app)


def response(success: bool = True, **kwargs):
    return {
        'status': 'ok' if success else 'error',
        **kwargs
    }

OK = response()
NOT_IMPLEMENTED = response(message='This feature is not implemented yet. Please check back later.')

#################### Generic ####################
@app.route('/login', methods=['POST'])
def login():
    username = json.loads(request.form['username'])

    if db.can_login(username):
        return OK
    return response(False, message='Invalid username')

@app.route('/log-query', methods=['POST'])
def log_query():
    username = json.loads(request.form['username'])
    query = json.loads(request.form['query'])
    success = json.loads(request.form['success'])

    query_id = db.log_query(
        username=username,
        query=query,
        success=success
    )

    return response(query_id=query_id)

@app.route('/message-feedback', methods=['POST'])
def feedback():
    message_id = json.loads(request.form['message_id'])
    feedback = json.loads(request.form['feedback'])

    db.log_feedback(
        message_id=message_id,
        feedback=feedback
    )

    return OK

#################### Syntax Error ####################
@app.route('/explain-error-message', methods=['POST'])
def explain_error_message():
    username = json.loads(request.form['username'])
    query_id = json.loads(request.form['query_id'])
    exception = json.loads(request.form['exception'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])
    
    query = db.get_query(query_id)
    answer = llm.explain_error_message(query, exception)

    db.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer)

@app.route('/locate-error-cause', methods=['POST'])
def locate_error_cause():
    query_id = json.loads(request.form['query_id'])
    exception = json.loads(request.form['exception'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])

    query = db.get_query(query_id)
    answer = llm.locate_error_cause(query, exception)

    db.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer)

@app.route('/provide-error-example', methods=['POST'])
def provide_error_example():
    # username = json.loads(request.form['username'])
    # query_id = json.loads(request.form['query_id'])
    # exception = json.loads(request.form['exception'])
    # chat_id = json.loads(request.form['chat_id'])
    # msg_id = json.loads(request.form['msg_id'])

    # query = db.get_query(query_id)
    # answer = llm.provide_error_example(query, exception)
    
    # db.log_button(
    #     query_id=query_id,
    #     content=answer
    #     button=request.path,
    #     data=None,
    #     chat_id=chat_id,
    #     msg_id=msg_id
    # )

    # return response(answer=answer)

    return NOT_IMPLEMENTED

@app.route('/fix-query', methods=['POST'])
def fix_query():
    query_id = json.loads(request.form['query_id'])
    exception = json.loads(request.form['exception'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])

    query = db.get_query(query_id)
    answer = llm.fix_query(query, exception)

    db.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=None,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer)

#################### Syntax OK ####################
@app.route('/describe-my-query', methods=['POST'])
def describe_my_query():
    query_id = json.loads(request.form['query_id'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])

    query = db.get_query(query_id)
    answer = llm.describe_my_query(query)

    db.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=None,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer)

@app.route('/explain-my-query', methods=['POST'])
def explain_my_query():
    query_id = json.loads(request.form['query_id'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])

    query = db.get_query(query_id)
    answer = llm.explain_my_query(query)

    db.log_message(
        query_id=query_id,
        content=answer,
        button=request.path,
        data=None,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return response(answer=answer)

##################### Help #####################
# @app.route('/list-users', methods=['POST'])
# def list_users():
#     username = json.loads(request.form['username'])

#     db.log_message(
#         username=username,
#         button=request.path,
#         data=None
#     )

#     return OK

# @app.route('/list-schemas', methods=['POST'])
# def list_schemas():
#     username = json.loads(request.form['username'])

#     db.log_message(
#         username=username,
#         button=request.path,
#         data=None
#     )

#     return OK

# @app.route('/list-tables', methods=['POST'])
# def list_tables():
#     username = json.loads(request.form['username'])

#     db.log_message(
#         username=username,
#         button=request.path,
#         data=None
#     )

#     return OK


###################### Main #####################

@app.route('/', methods=['GET'])
def start():
    with open('docker-compose.yml') as f:
        docker_compose = f.read()
    
    return docker_compose


if __name__ == '__main__':
    app.run(
    	host='0.0.0.0',
    	debug=True
    )
