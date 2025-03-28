from flask import Flask, request
from flask_cors import CORS


import json

import llm
import db


OK = { 'status': 'ok' }

app = Flask(__name__)
CORS(app)


@app.route('/login', methods=['POST'])
def login():
    username = json.loads(request.form['username'])

    if db.can_login(username):
        return OK
    return {
        'status': 'invalid_user',
    }

@app.route('/log-button', methods=['POST'])
def log_button():
    username = json.loads(request.form['username'])
    button = json.loads(request.form['button'])
    query = json.loads(request.form['query'])
    success = json.loads(request.form['success'])
    data = json.loads(request.form['data'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])

    db.log_button(
        username=username,
        button=button,
        query=query,
        success=success,
        data=data,
        chat_id=chat_id,
        msg_id=msg_id
    )

    return OK

@app.route('/log-query', methods=['POST'])
def log_query():
    username = json.loads(request.form['username'])
    query = json.loads(request.form['query'])
    success = json.loads(request.form['success'])

    db.log_query(
        username=username,
        query=query,
        success=success
    )

    return OK

@app.route('/explain-error-message', methods=['POST'])
def explain_error_message():
    username = json.loads(request.form['username'])
    query = json.loads(request.form['query'])
    exception = json.loads(request.form['exception'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])
    
    db.log_button(
        username=username,
        button='explain-error-message',
        query=query,
        success=False,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    answer = llm.explain_error_message(query, exception)

    return answer

@app.route('/identify-error-cause', methods=['POST'])
def identify_error_cause():
    username = json.loads(request.form['username'])
    query = json.loads(request.form['query'])
    exception = json.loads(request.form['exception'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])

    db.log_button(
        username=username,
        button='identify-error-cause',
        query=query,
        success=False,
        data=exception,
        chat_id=chat_id,
        msg_id=msg_id
    )

    answer = llm.identify_error_cause(query, exception)

    return answer


@app.route('/explain-my-query', methods=['POST'])
def explain_my_query():
    username = json.loads(request.form['username'])
    query = json.loads(request.form['query'])
    chat_id = json.loads(request.form['chat_id'])
    msg_id = json.loads(request.form['msg_id'])

    db.log_button(
        username=username,
        button='explain-my-query',
        query=query,
        success=False,
        data=None,
        chat_id=chat_id,
        msg_id=msg_id
    )

    answer = llm.explain_my_query(query)

    return answer


if __name__ == '__main__':
    app.run(
    	host='0.0.0.0',
    	debug=True
    )
