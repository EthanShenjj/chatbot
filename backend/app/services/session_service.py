"""Session service for CRUD operations and ownership validation."""
from typing import List, Optional
from app.models import db, Session, User
from sqlalchemy.exc import SQLAlchemyError


class SessionService:
    """Service for handling session operations."""
    
    @staticmethod
    def create_session(user_id: str, title: Optional[str] = None) -> Session:
        """
        Create a new session for a user.
        
        Args:
            user_id: User's unique identifier
            title: Optional session title
            
        Returns:
            Created Session object
            
        Raises:
            ValueError: If user does not exist
            SQLAlchemyError: If database operation fails
        """
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist")
        
        # Create new session
        session = Session(
            user_id=user_id,
            title=title
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session
    
    @staticmethod
    def get_user_sessions(user_id: str) -> List[Session]:
        """
        Get all sessions for a user ordered by most recent update time.
        
        Implements Requirement 1.5: Returns sessions ordered by updated_at DESC.
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            List of Session objects ordered by updated_at DESC
        """
        sessions = Session.query.filter_by(user_id=user_id)\
            .order_by(Session.updated_at.desc())\
            .all()
        
        return sessions
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session's unique identifier
            
        Returns:
            Session object or None if not found
        """
        return Session.query.get(session_id)
    
    @staticmethod
    def validate_session_ownership(session_id: str, user_id: str) -> bool:
        """
        Validate that a session belongs to a specific user.
        
        Implements Requirement 1.4: Validates session-user association.
        
        Args:
            session_id: Session's unique identifier
            user_id: User's unique identifier
            
        Returns:
            True if session belongs to user, False otherwise
        """
        session = Session.query.get(session_id)
        
        if not session:
            return False
        
        return session.user_id == user_id
    
    @staticmethod
    def update_session_title(session_id: str, title: str) -> Optional[Session]:
        """
        Update a session's title.
        
        Args:
            session_id: Session's unique identifier
            title: New title for the session
            
        Returns:
            Updated Session object or None if not found
        """
        session = Session.query.get(session_id)
        
        if not session:
            return None
        
        session.title = title
        db.session.commit()
        
        return session
    
    @staticmethod
    def delete_session(session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Args:
            session_id: Session's unique identifier
            
        Returns:
            True if session was deleted, False if not found
        """
        session = Session.query.get(session_id)
        
        if not session:
            return False
        
        db.session.delete(session)
        db.session.commit()
        
        return True
    
    @staticmethod
    def touch_session(session_id: str) -> None:
        """
        Update the session's updated_at timestamp.
        
        This is called when new messages are added to maintain proper ordering.
        
        Args:
            session_id: Session's unique identifier
        """
        session = Session.query.get(session_id)
        
        if session:
            # Force update of updated_at by modifying the session
            from datetime import datetime
            session.updated_at = datetime.utcnow()
            db.session.commit()
