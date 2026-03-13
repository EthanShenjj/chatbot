"""User model."""
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from . import db


class User(db.Model):
    """User model for authentication and session ownership."""
    
    __tablename__ = 'users'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sessions = relationship('Session', back_populates='user', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
