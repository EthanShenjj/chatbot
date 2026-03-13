"""Tests for JWT authentication middleware."""
import pytest
import json
from flask import Blueprint, jsonify
from app.services.auth_middleware import jwt_required_with_error_handling


# Create a test blueprint with protected route
test_bp = Blueprint('test_protected', __name__)


@test_bp.route('/protected', methods=['GET'])
@jwt_required_with_error_handling
def protected_route():
    """Test protected route."""
    return jsonify({'message': 'Access granted'}), 200


class TestAuthMiddleware:
    """Test JWT authentication middleware."""
    
    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Register test blueprint."""
        app.register_blueprint(test_bp)
    
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without JWT token."""
        response = client.get('/protected')
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert data['code'] in ['INVALID_TOKEN', 'AUTH_FAILED']
    
    def test_protected_route_with_valid_token(self, client):
        """Test accessing protected route with valid JWT token."""
        # Register and get token
        register_response = client.post(
            '/api/auth/register',
            data=json.dumps({
                'username': 'protecteduser',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        token = register_response.get_json()['access_token']
        
        # Access protected route with token
        response = client.get(
            '/protected',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Access granted'
    
    def test_protected_route_with_invalid_token(self, client):
        """Test accessing protected route with invalid JWT token."""
        response = client.get(
            '/protected',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert data['code'] in ['INVALID_TOKEN', 'AUTH_FAILED']
    
    def test_protected_route_with_malformed_header(self, client):
        """Test accessing protected route with malformed authorization header."""
        response = client.get(
            '/protected',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
