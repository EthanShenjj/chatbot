"""Message model."""
from sqlalchemy import Column, String, Text, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from . import db


class MessageRole(enum.Enum):
    """Message role enumeration."""
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'


class Message(db.Model):
    """Message model for conversation content with multimodal support."""
    
    __tablename__ = 'messages'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('sessions.id'), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(JSON, nullable=False)  # JSON array of content blocks
    raw_text = Column(Text)  # Extracted text for search and display
    interrupted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(3), default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    session = relationship('Session', back_populates='messages')
    
    def to_dict(self):
        """Convert message to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'role': self.role.value if isinstance(self.role, MessageRole) else self.role,
            'content': self.content,
            'raw_text': self.raw_text,
            'interrupted': self.interrupted,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
