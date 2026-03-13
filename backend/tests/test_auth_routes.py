"""Integration tests for authentication routes."""
import pytest
import json
from app.models import User, db


class TestAuthRoutes:
    """Test authentication API endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'testuser',
                'password': 'testpassword123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert 'user_id' in data
        assert data['access_token'] is not None
        assert data['user_id'] is not None
        
        # Verify user was created in database
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.username == 'testuser'
        assert user.password_hash is not None
    
    def test_register_duplicate_username(self, client):
        """Test registration with existing username."""
        # Create first user
        client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'duplicate',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        # Try to create second user with same username
        response = client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'duplicate',
                'password': 'different_password'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = response.get_json()
        assert data['code'] == 'USERNAME_EXISTS'
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        # Missing password
        response = client.post(
            '/api/auth/register',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'MISSING_FIELDS'
        
        # Missing username
        response = client.post(
            '/api/auth/register',
            data=json.dumps({'password': 'testpassword'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'MISSING_FIELDS'
    
    def test_register_empty_body(self, client):
        """Test registration with empty request body."""
        response = client.post(
            '/api/auth/register',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'INVALID_REQUEST'
    
    def test_login_success(self, client):
        """Test successful login."""
        # Register user first
        client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'loginuser',
                'password': 'loginpassword123'
            }),
            content_type='application/json'
        )
        
        # Login with correct credentials
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'loginuser',
                'password': 'loginpassword123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user_id' in data
        assert 'username' in data
        assert data['username'] == 'loginuser'
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent username."""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'nonexistent',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 'INVALID_CREDENTIALS'
    
    def test_login_invalid_password(self, client):
        """Test login with incorrect password."""
        # Register user first
        client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'wrongpassuser',
                'password': 'correctpassword'
            }),
            content_type='application/json'
        )
        
        # Try to login with wrong password
        response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'username': 'wrongpassuser',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['code'] == 'INVALID_CREDENTIALS'
    
    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        # Missing password
        response = client.post(
            '/api/auth/login',
            data=json.dumps({'username': 'testuser'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['code'] == 'MISSING_FIELDS'
    
    def test_jwt_token_valid_format(self, client):
        """Test that JWT token has valid format."""
        response = client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'jwtuser',
                'password': 'jwtpassword'
            }),
            content_type='application/json'
        )
        
        data = response.get_json()
        token = data['access_token']
        
        # JWT tokens have 3 parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3
