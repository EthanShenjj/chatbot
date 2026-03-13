"""Flask application factory."""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import sys
import os

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from app.models import db
from app.middleware import register_error_handlers

jwt = JWTManager()


def create_app(config_class=Config):
    """Create and configure the Flask application.
    
    Validates configuration at startup and refuses to start if required
    configuration is missing (Requirements 19.2, 19.3).
    """
    # Validate configuration before creating app (Requirement 19.2, 19.3)
    try:
        config_class.validate()
    except ValueError as e:
        # Log error and refuse to start (Requirement 19.3)
        import logging
        logging.error(f"Configuration validation failed: {e}")
        raise
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS with explicit settings
    CORS(app, 
         resources={r"/api/*": {
             "origins": app.config['CORS_ORIGINS'],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Type", "Authorization"]
         }})
    
    # Register error handlers
    register_error_handlers(app)
    
    # Add security headers
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Create upload folder if it doesn't exist
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    
    # Serve uploaded files as static content
    from flask import send_from_directory
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files."""
        return send_from_directory(upload_folder, filename)
    
    # Register blueprints
    from app.routes import auth, sessions, chat, upload
    app.register_blueprint(auth.bp)
    app.register_blueprint(sessions.bp)
    app.register_blueprint(chat.bp)
    app.register_blueprint(upload.bp)
    
    return app
