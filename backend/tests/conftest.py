"""Pytest configuration and fixtures for tests."""
import pytest
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import create_app
from config import Config


class TestConfig(Config):
    """Test configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = create_app(TestConfig)
    
    with app.app_context():
        yield app


@pytest.fixture
def app_context(app):
    """Provide Flask application context for tests."""
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    from app.models import db
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def auth_headers(client):
    """Create a test user and return authentication headers."""
    from app.models import db, User
    from app.services.auth_service import AuthService
    from flask_jwt_extended import create_access_token
    
    # Create test user
    user = User(
        username='testuser',
        password_hash=AuthService.hash_password('testpassword')
    )
    db.session.add(user)
    db.session.commit()
    
    # Generate JWT token
    access_token = create_access_token(identity=user.id)
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
