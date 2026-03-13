"""Tests for message service."""
import pytest
from app.models import db, Message, Session, User, MessageRole
from app.services.message_service import MessageService
from app.services.auth_service import AuthService


class TestMessageService:
    """Test cases for MessageService."""
    
    def test_create_message_with_text_content(self, client):
        """Test creating a message with text content."""
        # Create user and session
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        # Create message
        message = MessageService.create_message(
            session_id=session.id,
            role='user',
            content='Hello, world!'
        )
        
        assert message.id is not None
        assert message.session_id == session.id
        assert message.role == MessageRole.USER
        assert len(message.content) == 1
        assert message.content[0]['type'] == 'text'
        assert message.content[0]['text'] == 'Hello, world!'
        assert message.raw_text == 'Hello, world!'
        assert message.interrupted is False
    
    def test_create_message_with_content_blocks(self, client):
        """Test creating a message with structured content blocks."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        content = [
            {'type': 'text', 'text': 'Check this image:'},
            {'type': 'image_url', 'image_url': {'url': 'https://example.com/image.png'}}
        ]
        
        message = MessageService.create_message(
            session_id=session.id,
            role='user',
            content=content
        )
        
        assert len(message.content) == 2
        assert message.content[0]['type'] == 'text'
        assert message.content[1]['type'] == 'image_url'
        assert message.raw_text == 'Check this image:'
    
    def test_create_message_with_interrupted_flag(self, client):
        """Test creating an interrupted message."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        message = MessageService.create_message(
            session_id=session.id,
            role='assistant',
            content='Partial response...',
            interrupted=True
        )
        
        assert message.interrupted is True
    
    def test_create_message_invalid_session(self, client):
        """Test creating a message with invalid session ID."""
        with pytest.raises(ValueError, match='Session with id .* does not exist'):
            MessageService.create_message(
                session_id='invalid-id',
                role='user',
                content='Test'
            )
    
    def test_create_message_invalid_role(self, client):
        """Test creating a message with invalid role."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        with pytest.raises(ValueError, match='Invalid role'):
            MessageService.create_message(
                session_id=session.id,
                role='invalid_role',
                content='Test'
            )
    
    def test_create_message_invalid_content(self, client):
        """Test creating a message with invalid content."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        with pytest.raises(ValueError, match='Invalid message content'):
            MessageService.create_message(
                session_id=session.id,
                role='user',
                content=[{'type': 'invalid_type'}]
            )
    
    def test_get_session_messages(self, client):
        """Test retrieving messages for a session."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        # Create multiple messages
        msg1 = MessageService.create_message(session.id, 'user', 'First message')
        msg2 = MessageService.create_message(session.id, 'assistant', 'Second message')
        msg3 = MessageService.create_message(session.id, 'user', 'Third message')
        
        # Retrieve messages
        messages = MessageService.get_session_messages(session.id)
        
        assert len(messages) == 3
        assert messages[0].id == msg1.id
        assert messages[1].id == msg2.id
        assert messages[2].id == msg3.id
    
    def test_get_message(self, client):
        """Test retrieving a single message by ID."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        created_message = MessageService.create_message(
            session.id, 'user', 'Test message'
        )
        
        retrieved_message = MessageService.get_message(created_message.id)
        
        assert retrieved_message is not None
        assert retrieved_message.id == created_message.id
        assert retrieved_message.raw_text == 'Test message'
    
    def test_get_message_not_found(self, client):
        """Test retrieving a non-existent message."""
        message = MessageService.get_message('invalid-id')
        assert message is None
    
    def test_mark_interrupted(self, client):
        """Test marking a message as interrupted."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        message = MessageService.create_message(
            session.id, 'assistant', 'Partial response'
        )
        
        assert message.interrupted is False
        
        updated_message = MessageService.mark_interrupted(message.id)
        
        assert updated_message.interrupted is True
    
    def test_mark_interrupted_not_found(self, client):
        """Test marking a non-existent message as interrupted."""
        result = MessageService.mark_interrupted('invalid-id')
        assert result is None
    
    def test_update_message_content(self, client):
        """Test updating message content."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        message = MessageService.create_message(
            session.id, 'user', 'Original content'
        )
        
        updated_message = MessageService.update_message_content(
            message.id, 'Updated content'
        )
        
        assert updated_message.raw_text == 'Updated content'
        assert updated_message.content[0]['text'] == 'Updated content'
    
    def test_delete_message(self, client):
        """Test deleting a message."""
        user = User(username='testuser', password_hash=AuthService.hash_password('password'))
        db.session.add(user)
        db.session.commit()
        
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        message = MessageService.create_message(
            session.id, 'user', 'Test message'
        )
        
        result = MessageService.delete_message(message.id)
        assert result is True
        
        # Verify message is deleted
        retrieved = MessageService.get_message(message.id)
        assert retrieved is None
    
    def test_delete_message_not_found(self, client):
        """Test deleting a non-existent message."""
        result = MessageService.delete_message('invalid-id')
        assert result is False
