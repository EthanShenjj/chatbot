"""JWT authentication middleware for protected routes."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError


def jwt_required_with_error_handling(fn):
    """
    Decorator for protecting routes with JWT authentication.
    
    Returns 401 error if JWT token is expired or invalid as per Requirement 16.5.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except ExpiredSignatureError:
            return jsonify({
                'error': 'JWT token has expired',
                'code': 'TOKEN_EXPIRED'
            }), 401
        except InvalidTokenError:
            return jsonify({
                'error': 'Invalid JWT token',
                'code': 'INVALID_TOKEN'
            }), 401
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_FAILED'
            }), 401
    
    return wrapper
