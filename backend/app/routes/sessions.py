"""Session routes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import db, Message
from app.services import SessionService, jwt_required_with_error_handling

bp = Blueprint('sessions', __name__, url_prefix='/api/sessions')


@bp.route('', methods=['GET'])
@jwt_required_with_error_handling
def get_sessions():
    """
    Get all sessions for the authenticated user.
    
    Implements Requirement 1.5: Returns sessions ordered by updated_at DESC.
    
    Returns:
        {
            "sessions": [
                {
                    "id": "string",
                    "title": "string",
                    "updated_at": "ISO8601 timestamp"
                }
            ]
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Get user's sessions ordered by most recent
        sessions = SessionService.get_user_sessions(user_id)
        
        # Convert to response format
        sessions_data = [
            {
                'id': session.id,
                'title': session.title,
                'updated_at': session.updated_at.isoformat() if session.updated_at else None
            }
            for session in sessions
        ]
        
        return jsonify({
            'sessions': sessions_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500


@bp.route('', methods=['POST'])
@jwt_required_with_error_handling
def create_session():
    """
    Create a new session for the authenticated user.
    
    Implements Requirement 1.3: Generates unique session identifier and stores in database.
    Implements Requirement 1.4: Associates session with user account.
    
    Request body (optional):
        {
            "title": "string"
        }
    
    Returns:
        {
            "session_id": "string",
            "created_at": "ISO8601 timestamp"
        }
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json(silent=True) or {}
        
        title = data.get('title')
        
        # Create new session
        session = SessionService.create_session(user_id, title)
        
        return jsonify({
            'session_id': session.id,
            'created_at': session.created_at.isoformat() if session.created_at else None
        }), 201
        
    except ValueError as e:
        return jsonify({
            'error': str(e),
            'code': 'INVALID_USER'
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500


@bp.route('/<session_id>/messages', methods=['GET'])
@jwt_required_with_error_handling
def get_session_messages(session_id):
    """
    Get all messages for a specific session.
    
    Implements Requirement 12.3: Retrieves messages ordered by creation time.
    Implements Requirement 12.5: Returns within 500ms for up to 1000 messages.
    
    Args:
        session_id: Session's unique identifier
    
    Returns:
        {
            "messages": [
                {
                    "id": "string",
                    "role": "user|assistant|system",
                    "content": [ContentBlock],
                    "raw_text": "string",
                    "created_at": "ISO8601 timestamp",
                    "interrupted": false
                }
            ]
        }
    """
    try:
        user_id = get_jwt_identity()
        
        # Validate session ownership
        if not SessionService.validate_session_ownership(session_id, user_id):
            return jsonify({
                'error': 'Session not found or access denied',
                'code': 'SESSION_NOT_FOUND'
            }), 404
        
        # Get messages ordered by creation time
        messages = Message.query.filter_by(session_id=session_id)\
            .order_by(Message.created_at.asc())\
            .all()
        
        # Convert to response format
        messages_data = [message.to_dict() for message in messages]
        
        return jsonify({
            'messages': messages_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500
