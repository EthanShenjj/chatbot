"""Message service for CRUD operations."""
from typing import List, Optional, Union, Dict, Any
from app.models import db, Message, Session, MessageRole
from app.services.message_parser import MessageParser
from sqlalchemy.exc import SQLAlchemyError
import logging


logger = logging.getLogger(__name__)


class MessageService:
    """Service for handling message operations."""
    
    @staticmethod
    def create_message(
        session_id: str,
        role: str,
        content: Union[str, List[Dict[str, Any]]],
        raw_text: Optional[str] = None,
        interrupted: bool = False
    ) -> Message:
        """
        Create a new message in a session.
        
        Args:
            session_id: Session's unique identifier
            role: Message role ('user', 'assistant', or 'system')
            content: Message content (string or list of content blocks)
            raw_text: Optional pre-extracted raw text (will be extracted if not provided)
            interrupted: Whether the message was interrupted during streaming
            
        Returns:
            Created Message object
            
        Raises:
            ValueError: If session does not exist or content is invalid
            SQLAlchemyError: If database operation fails
        """
        # Validate session exists
        session = Session.query.get(session_id)
        if not session:
            raise ValueError(f"Session with id {session_id} does not exist")
        
        # Parse and validate content
        try:
            # If content is a string, convert to text content block
            if isinstance(content, str):
                content = [{'type': 'text', 'text': content}]
            
            # Validate content structure
            parsed_content = MessageParser.parse_content(content)
            
            # Extract raw text if not provided
            if raw_text is None:
                raw_text = MessageParser.extract_raw_text(parsed_content)
            
        except Exception as e:
            raise ValueError(f"Invalid message content: {str(e)}")
        
        # Convert role string to enum
        try:
            role_enum = MessageRole[role.upper()]
        except KeyError:
            raise ValueError(f"Invalid role: {role}. Must be 'user', 'assistant', or 'system'")
        
        # Create message
        message = Message(
            session_id=session_id,
            role=role_enum,
            content=parsed_content,
            raw_text=raw_text,
            interrupted=interrupted
        )
        
        db.session.add(message)
        db.session.commit()
        
        # Update session's updated_at timestamp
        from app.services.session_service import SessionService
        SessionService.touch_session(session_id)
        
        logger.info(f"Created message {message.id} in session {session_id}")
        
        return message
    
    @staticmethod
    def get_session_messages(session_id: str) -> List[Message]:
        """
        Get all messages for a session ordered by creation time.
        
        Implements Requirement 12.3: Returns messages ordered by created_at ASC.
        
        Args:
            session_id: Session's unique identifier
            
        Returns:
            List of Message objects ordered by created_at ASC
        """
        messages = Message.query.filter_by(session_id=session_id)\
            .order_by(Message.created_at.asc())\
            .all()
        
        return messages
    
    @staticmethod
    def get_message(message_id: str) -> Optional[Message]:
        """
        Get a message by ID.
        
        Args:
            message_id: Message's unique identifier
            
        Returns:
            Message object or None if not found
        """
        return Message.query.get(message_id)
    
    @staticmethod
    def update_message_content(
        message_id: str,
        content: Union[str, List[Dict[str, Any]]],
        raw_text: Optional[str] = None
    ) -> Optional[Message]:
        """
        Update a message's content.
        
        Args:
            message_id: Message's unique identifier
            content: New message content
            raw_text: Optional pre-extracted raw text
            
        Returns:
            Updated Message object or None if not found
        """
        message = Message.query.get(message_id)
        
        if not message:
            return None
        
        # Parse and validate content
        try:
            if isinstance(content, str):
                content = [{'type': 'text', 'text': content}]
            
            parsed_content = MessageParser.parse_content(content)
            
            if raw_text is None:
                raw_text = MessageParser.extract_raw_text(parsed_content)
            
            message.content = parsed_content
            message.raw_text = raw_text
            
            db.session.commit()
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to update message {message_id}: {e}")
            return None
    
    @staticmethod
    def mark_interrupted(message_id: str) -> Optional[Message]:
        """
        Mark a message as interrupted.
        
        Implements Requirement 5.4: Mark interrupted messages with flag.
        
        Args:
            message_id: Message's unique identifier
            
        Returns:
            Updated Message object or None if not found
        """
        message = Message.query.get(message_id)
        
        if not message:
            return None
        
        message.interrupted = True
        db.session.commit()
        
        logger.info(f"Marked message {message_id} as interrupted")
        
        return message
    
    @staticmethod
    def delete_message(message_id: str) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: Message's unique identifier
            
        Returns:
            True if message was deleted, False if not found
        """
        message = Message.query.get(message_id)
        
        if not message:
            return False
        
        db.session.delete(message)
        db.session.commit()
        
        return True
