"""Authentication routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User
from app.services import AuthService

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user account.
    
    Request body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        {
            "access_token": "string",
            "user_id": "string"
        }
    """
    try:
        data = request.get_json(silent=True)
        
        # Validate input
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'INVALID_REQUEST'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'error': 'Username and password are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'error': 'Username already exists',
                'code': 'USERNAME_EXISTS'
            }), 409
        
        # Hash password and create user
        password_hash = AuthService.hash_password(password)
        new_user = User(
            username=username,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate JWT token
        access_token = AuthService.generate_token(new_user.id, new_user.username)
        
        return jsonify({
            'access_token': access_token,
            'user_id': new_user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    Login with existing credentials.
    
    Request body:
        {
            "username": "string",
            "password": "string"
        }
    
    Returns:
        {
            "access_token": "string",
            "user_id": "string",
            "username": "string"
        }
    """
    try:
        data = request.get_json(silent=True)
        
        # Validate input
        if not data:
            return jsonify({
                'error': 'Request body is required',
                'code': 'INVALID_REQUEST'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'error': 'Username and password are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        # Find user by username
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({
                'error': 'Invalid username or password',
                'code': 'INVALID_CREDENTIALS'
            }), 401
        
        # Verify password
        if not AuthService.verify_password(password, user.password_hash):
            return jsonify({
                'error': 'Invalid username or password',
                'code': 'INVALID_CREDENTIALS'
            }), 401
        
        # Generate JWT token
        access_token = AuthService.generate_token(user.id, user.username)
        
        return jsonify({
            'access_token': access_token,
            'user_id': user.id,
            'username': user.username
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500
