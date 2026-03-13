"""Error handling middleware for structured error responses."""
import logging
from flask import jsonify
from werkzeug.exceptions import HTTPException
import requests
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base class for API errors."""
    
    def __init__(self, message, status_code=500, error_code=None, retry_after=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'SERVER_ERROR'
        self.retry_after = retry_after


class LLMConnectionError(APIError):
    """Error when LLM provider connection fails."""
    
    def __init__(self, message="Cannot connect to LLM provider", retry_after=60):
        super().__init__(
            message=message,
            status_code=503,
            error_code='LLM_CONNECTION_ERROR',
            retry_after=retry_after
        )


class AuthenticationError(APIError):
    """Error when authentication fails."""
    
    def __init__(self, message="Authentication failed"):
        super().__init__(
            message=message,
            status_code=401,
            error_code='AUTHENTICATION_ERROR'
        )


def register_error_handlers(app):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors."""
        logger.error(
            f"API Error: {error.error_code} - {error.message}",
            extra={
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status_code': error.status_code,
                'error_code': error.error_code
            }
        )
        
        response = jsonify({
            'error': error.message,
            'code': error.error_code
        })
        response.status_code = error.status_code
        
        if error.retry_after:
            response.headers['Retry-After'] = str(error.retry_after)
        
        return response
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle Werkzeug HTTP exceptions."""
        logger.warning(
            f"HTTP Exception: {error.code} - {error.description}",
            extra={
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'status_code': error.code
            }
        )
        
        response = jsonify({
            'error': error.description,
            'code': f'HTTP_{error.code}'
        })
        response.status_code = error.code
        return response
    
    @app.errorhandler(requests.exceptions.RequestException)
    def handle_requests_exception(error):
        """Handle requests library exceptions (LLM provider errors)."""
        logger.error(
            f"LLM Provider Error: {str(error)}",
            extra={
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error_type': type(error).__name__
            }
        )
        
        # Determine if it's a connection error
        if isinstance(error, (requests.exceptions.ConnectionError, 
                            requests.exceptions.Timeout)):
            response = jsonify({
                'error': 'Cannot connect to LLM provider. Please try again later.',
                'code': 'LLM_CONNECTION_ERROR'
            })
            response.status_code = 503
            response.headers['Retry-After'] = '60'
        else:
            response = jsonify({
                'error': 'LLM provider error occurred',
                'code': 'LLM_ERROR'
            })
            response.status_code = 503
        
        return response
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all other exceptions."""
        logger.error(
            f"Unhandled Exception: {str(error)}",
            extra={
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'error_type': type(error).__name__
            },
            exc_info=True
        )
        
        response = jsonify({
            'error': 'An internal server error occurred',
            'code': 'SERVER_ERROR'
        })
        response.status_code = 500
        return response
