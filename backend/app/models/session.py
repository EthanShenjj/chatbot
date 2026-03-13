"""Session model."""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from . import db


class Session(db.Model):
    """Session model for conversation threads."""
    
    __tablename__ = 'sessions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(255))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='sessions')
    messages = relationship('Message', back_populates='session', cascade='all, delete-orphan', order_by='Message.created_at')
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
