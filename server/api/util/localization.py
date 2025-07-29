from flask import request

def get_locale():
    '''Return the language currently set by the client.'''
    
    return request.headers.get('X-Language', 'en')
