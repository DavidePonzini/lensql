from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_babel import Babel
import os

from .util import localization
from server import db

jwt = JWTManager()
babel = Babel()

def create_app() -> Flask:
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'key')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 1024*1024*20))   # 20MB
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../locales'  # Relative path starts from the app root, which is this file's directory

    # Setup CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])
    
    # Setup localization
    babel.init_app(app, locale_selector=localization.get_locale)

    # Setup JWT
    jwt.init_app(app)

    # Register blueprints
    from . import auth, datasets, exercises, messages, queries, users, classes

    app.register_blueprint(classes.bp, url_prefix='/classes')
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(datasets.bp, url_prefix='/datasets')
    app.register_blueprint(exercises.bp, url_prefix='/exercises')
    app.register_blueprint(messages.bp, url_prefix='/messages')
    app.register_blueprint(queries.bp, url_prefix='/queries')
    app.register_blueprint(users.bp, url_prefix='/users')

    # Run cleanup thread
    if os.getenv('GUNICORN_WORKER_ID', '0') == '0':
        db.users.start_cleanup_thread()


    return app

