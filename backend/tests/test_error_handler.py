"""Tests for error handling middleware."""
import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
import requests
from werkzeug.exceptions import NotFound, BadRequest
from app.middleware.error_handler import (
    APIError,
    LLMConnectionError,
    AuthenticationError,
    register_error_handlers
)


class TestAPIError:
    """Test custom API error classes."""
    
    def test_api_error_default_values(self):
        """Test APIError with default values."""
        error = APIError("Test error")
        assert error.message == "Test error"
        assert error.status_code == 500
        assert error.error_code == "SERVER_ERROR"
        assert error.retry_after is None
    
    def test_api_error_custom_values(self):
        """Test APIError with custom values."""
        error = APIError(
            "Custom error",
            status_code=400,
            error_code="CUSTOM_ERROR",
            retry_after=30
        )
        assert error.message == "Custom error"
        assert error.status_code == 400
        assert error.error_code == "CUSTOM_ERROR"
        assert error.retry_after == 30
    
    def test_llm_connection_error_defaults(self):
        """Test LLMConnectionError with default values."""
        error = LLMConnectionError()
        assert error.message == "Cannot connect to LLM provider"
        assert error.status_code == 503
        assert error.error_code == "LLM_CONNECTION_ERROR"
        assert error.retry_after == 60
    
    def test_llm_connection_error_custom_message(self):
        """Test LLMConnectionError with custom message and retry."""
        error = LLMConnectionError("Custom LLM error", retry_after=120)
        assert error.message == "Custom LLM error"
        assert error.status_code == 503
        assert error.error_code == "LLM_CONNECTION_ERROR"
        assert error.retry_after == 120
    
    def test_authentication_error_defaults(self):
        """Test AuthenticationError with default values."""
        error = AuthenticationError()
        assert error.message == "Authentication failed"
        assert error.status_code == 401
        assert error.error_code == "AUTHENTICATION_ERROR"
        assert error.retry_after is None
    
    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message."""
        error = AuthenticationError("Invalid token")
        assert error.message == "Invalid token"
        assert error.status_code == 401
        assert error.error_code == "AUTHENTICATION_ERROR"


class TestErrorHandlers:
    """Test error handler middleware."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app with error handlers."""
        from flask import Flask
        app = Flask(__name__)
        app.config['TESTING'] = True
        register_error_handlers(app)
        
        # Add test routes that raise errors
        @app.route('/test/api-error')
        def test_api_error():
            raise APIError("Test API error", status_code=400, error_code="TEST_ERROR")
        
        @app.route('/test/llm-connection-error')
        def test_llm_connection_error():
            raise LLMConnectionError("LLM unavailable", retry_after=30)
        
        @app.route('/test/auth-error')
        def test_auth_error():
            raise AuthenticationError("Invalid credentials")
        
        @app.route('/test/http-exception')
        def test_http_exception():
            raise NotFound("Resource not found")
        
        @app.route('/test/requests-connection-error')
        def test_requests_connection_error():
            raise requests.exceptions.ConnectionError("Connection failed")
        
        @app.route('/test/requests-timeout')
        def test_requests_timeout():
            raise requests.exceptions.Timeout("Request timeout")
        
        @app.route('/test/requests-other-error')
        def test_requests_other_error():
            raise requests.exceptions.RequestException("Other request error")
        
        @app.route('/test/generic-exception')
        def test_generic_exception():
            raise ValueError("Unexpected error")
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_api_error_handler(self, client):
        """Test handling of APIError - structured error response."""
        response = client.get('/test/api-error')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == "Test API error"
        assert data['code'] == "TEST_ERROR"
    
    def test_llm_connection_error_handler(self, client):
        """Test handling of LLMConnectionError - 503 with retry-after header.
        
        **Validates: Requirements 13.1, 13.2**
        """
        response = client.get('/test/llm-connection-error')
        
        # Requirement 13.2: 503 status code
        assert response.status_code == 503
        
        # Requirement 13.1: Structured error response
        data = json.loads(response.data)
        assert data['error'] == "LLM unavailable"
        assert data['code'] == "LLM_CONNECTION_ERROR"
        
        # Requirement 13.2: Retry-After header
        assert 'Retry-After' in response.headers
        assert response.headers['Retry-After'] == '30'
    
    def test_authentication_error_handler(self, client):
        """Test handling of AuthenticationError - 401 with clear reason.
        
        **Validates: Requirements 13.1, 13.3**
        """
        response = client.get('/test/auth-error')
        
        # Requirement 13.3: 401 status code
        assert response.status_code == 401
        
        # Requirement 13.1: Structured error response
        data = json.loads(response.data)
        assert data['error'] == "Invalid credentials"
        assert data['code'] == "AUTHENTICATION_ERROR"
    
    def test_http_exception_handler(self, client):
        """Test handling of Werkzeug HTTP exceptions."""
        response = client.get('/test/http-exception')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert data['code'] == 'HTTP_404'
    
    def test_requests_connection_error_handler(self, client):
        """Test handling of requests ConnectionError - 503 with retry-after.
        
        **Validates: Requirements 13.1, 13.2**
        """
        response = client.get('/test/requests-connection-error')
        
        # Requirement 13.2: 503 status code for connection failures
        assert response.status_code == 503
        
        # Requirement 13.1: Structured error response
        data = json.loads(response.data)
        assert 'Cannot connect to LLM provider' in data['error']
        assert data['code'] == 'LLM_CONNECTION_ERROR'
        
        # Requirement 13.2: Retry-After header
        assert 'Retry-After' in response.headers
        assert response.headers['Retry-After'] == '60'
    
    def test_requests_timeout_handler(self, client):
        """Test handling of requests Timeout - 503 with retry-after.
        
        **Validates: Requirements 13.1, 13.2**
        """
        response = client.get('/test/requests-timeout')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert 'Cannot connect to LLM provider' in data['error']
        assert data['code'] == 'LLM_CONNECTION_ERROR'
        assert 'Retry-After' in response.headers
    
    def test_requests_other_error_handler(self, client):
        """Test handling of other requests exceptions."""
        response = client.get('/test/requests-other-error')
        
        assert response.status_code == 503
        data = json.loads(response.data)
        assert data['error'] == 'LLM provider error occurred'
        assert data['code'] == 'LLM_ERROR'
    
    def test_generic_exception_handler(self, client):
        """Test handling of unexpected exceptions."""
        response = client.get('/test/generic-exception')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['error'] == 'An internal server error occurred'
        assert data['code'] == 'SERVER_ERROR'
    
    @patch('app.middleware.error_handler.logger')
    def test_error_logging_with_timestamp(self, mock_logger, client):
        """Test that errors are logged with timestamp and context.
        
        **Validates: Requirement 13.5**
        """
        # Trigger an API error
        client.get('/test/api-error')
        
        # Verify logging was called
        assert mock_logger.error.called
        
        # Check log message contains error details
        call_args = mock_logger.error.call_args
        log_message = call_args[0][0]
        assert "TEST_ERROR" in log_message
        assert "Test API error" in log_message
        
        # Requirement 13.5: Check timestamp in extra context
        extra = call_args[1].get('extra', {})
        assert 'timestamp' in extra
        assert 'status_code' in extra
        assert 'error_code' in extra
        
        # Verify timestamp format (ISO 8601)
        timestamp = extra['timestamp']
        datetime.fromisoformat(timestamp)  # Should not raise
    
    @patch('app.middleware.error_handler.logger')
    def test_llm_error_logging_with_context(self, mock_logger, client):
        """Test LLM errors are logged with context information.
        
        **Validates: Requirement 13.5**
        """
        # Trigger an LLM connection error
        client.get('/test/requests-connection-error')
        
        # Verify logging was called
        assert mock_logger.error.called
        
        # Check log contains context
        call_args = mock_logger.error.call_args
        extra = call_args[1].get('extra', {})
        
        # Requirement 13.5: Timestamp and context
        assert 'timestamp' in extra
        assert 'error_type' in extra
        assert extra['error_type'] == 'ConnectionError'
    
    @patch('app.middleware.error_handler.logger')
    def test_authentication_error_logging(self, mock_logger, client):
        """Test authentication errors are logged properly.
        
        **Validates: Requirement 13.5**
        """
        # Trigger an authentication error
        client.get('/test/auth-error')
        
        # Verify logging was called
        assert mock_logger.error.called
        
        # Check log message
        call_args = mock_logger.error.call_args
        log_message = call_args[0][0]
        assert "AUTHENTICATION_ERROR" in log_message
        
        # Check context
        extra = call_args[1].get('extra', {})
        assert 'timestamp' in extra
        assert 'status_code' in extra
        assert extra['status_code'] == 401


class TestErrorHandlerIntegration:
    """Integration tests for error handling in real scenarios."""
    
    @pytest.fixture
    def app(self):
        """Create test Flask app."""
        from flask import Flask, jsonify
        from flask_jwt_extended import JWTManager, jwt_required, create_access_token
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['JWT_SECRET_KEY'] = 'test-secret'
        
        jwt = JWTManager(app)
        register_error_handlers(app)
        
        @app.route('/test/protected')
        @jwt_required()
        def protected_route():
            return jsonify({'message': 'success'})
        
        @app.route('/test/login')
        def login():
            token = create_access_token(identity='test-user')
            return jsonify({'token': token})
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_jwt_authentication_failure(self, client):
        """Test JWT authentication failure returns 401.
        
        **Validates: Requirement 13.3**
        """
        # Try to access protected route without token
        response = client.get('/test/protected')
        
        # Should return 401 (handled by Flask-JWT-Extended)
        assert response.status_code == 401
