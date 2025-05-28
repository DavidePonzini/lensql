from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

from server import db


jwt = JWTManager()


def create_app() -> Flask:
    """Create and configure the Flask application."""
    
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'key')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 1024*1024*20))   # 20MB

    CORS(app)
    jwt.init_app(app)

    # Register blueprints
    from .assignments import assignment_bp
    from .auth import auth_bp
    from .datasets import dataset_bp
    from .exercises import exercise_bp
    from .messages import message_bp
    from .queries import query_bp
    from .users import user_bp

    app.register_blueprint(assignment_bp, url_prefix='/assignments')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dataset_bp, url_prefix='/datasets')
    app.register_blueprint(exercise_bp, url_prefix='/exercises')
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(query_bp, url_prefix='/queries')
    app.register_blueprint(user_bp, url_prefix='/users')

    # Run cleanup thread
    if os.getenv('GUNICORN_WORKER_ID', '0') == '0':
        db.users.start_cleanup_thread()


    return app

