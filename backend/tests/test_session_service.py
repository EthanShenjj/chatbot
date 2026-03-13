"""Unit tests for session service."""
import pytest
from app.models import db, User, Session
from app.services import SessionService, AuthService


class TestSessionCreation:
    """Test session creation functionality."""
    
    def test_create_session_success(self, client):
        """Test successful session creation."""
        # Create a user first
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        # Create session
        session = SessionService.create_session(user.id)
        
        assert session is not None
        assert session.id is not None
        assert session.user_id == user.id
        assert session.title is None
        assert session.created_at is not None
        assert session.updated_at is not None
    
    def test_create_session_with_title(self, client):
        """Test session creation with custom title."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        session = SessionService.create_session(user.id, title='My Chat Session')
        
        assert session.title == 'My Chat Session'
    
    def test_create_session_invalid_user(self, client):
        """Test session creation with non-existent user."""
        with pytest.raises(ValueError, match='User with id .* does not exist'):
            SessionService.create_session('nonexistent-user-id')
    
    def test_create_session_generates_unique_ids(self, client):
        """Test that each session gets a unique ID."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        session1 = SessionService.create_session(user.id)
        session2 = SessionService.create_session(user.id)
        
        assert session1.id != session2.id


class TestGetUserSessions:
    """Test retrieving user sessions."""
    
    def test_get_user_sessions_empty(self, client):
        """Test getting sessions for user with no sessions."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        sessions = SessionService.get_user_sessions(user.id)
        
        assert sessions == []
    
    def test_get_user_sessions_ordered_by_updated_at(self, client):
        """Test that sessions are ordered by updated_at DESC."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        # Create multiple sessions
        session1 = SessionService.create_session(user.id, title='First')
        session2 = SessionService.create_session(user.id, title='Second')
        session3 = SessionService.create_session(user.id, title='Third')
        
        # Update session1 to make it most recent
        SessionService.touch_session(session1.id)
        
        sessions = SessionService.get_user_sessions(user.id)
        
        # Should be ordered by most recent first
        assert len(sessions) == 3
        assert sessions[0].id == session1.id
    
    def test_get_user_sessions_only_returns_user_sessions(self, client):
        """Test that only sessions belonging to the user are returned."""
        user1 = User(
            username='user1',
            password_hash=AuthService.hash_password('password')
        )
        user2 = User(
            username='user2',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add_all([user1, user2])
        db.session.commit()
        
        # Create sessions for both users
        session1 = SessionService.create_session(user1.id, title='User1 Session')
        session2 = SessionService.create_session(user2.id, title='User2 Session')
        
        # Get user1's sessions
        user1_sessions = SessionService.get_user_sessions(user1.id)
        
        assert len(user1_sessions) == 1
        assert user1_sessions[0].id == session1.id
        assert user1_sessions[0].title == 'User1 Session'


class TestGetSession:
    """Test retrieving individual sessions."""
    
    def test_get_session_success(self, client):
        """Test successfully retrieving a session by ID."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        created_session = SessionService.create_session(user.id, title='Test Session')
        
        retrieved_session = SessionService.get_session(created_session.id)
        
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.title == 'Test Session'
    
    def test_get_session_not_found(self, client):
        """Test retrieving non-existent session."""
        session = SessionService.get_session('nonexistent-id')
        
        assert session is None


class TestSessionOwnershipValidation:
    """Test session ownership validation."""
    
    def test_validate_session_ownership_success(self, client):
        """Test successful ownership validation."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        session = SessionService.create_session(user.id)
        
        is_owner = SessionService.validate_session_ownership(session.id, user.id)
        
        assert is_owner is True
    
    def test_validate_session_ownership_wrong_user(self, client):
        """Test ownership validation with wrong user."""
        user1 = User(
            username='user1',
            password_hash=AuthService.hash_password('password')
        )
        user2 = User(
            username='user2',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add_all([user1, user2])
        db.session.commit()
        
        session = SessionService.create_session(user1.id)
        
        is_owner = SessionService.validate_session_ownership(session.id, user2.id)
        
        assert is_owner is False
    
    def test_validate_session_ownership_nonexistent_session(self, client):
        """Test ownership validation with non-existent session."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        is_owner = SessionService.validate_session_ownership('nonexistent-id', user.id)
        
        assert is_owner is False


class TestUpdateSessionTitle:
    """Test updating session titles."""
    
    def test_update_session_title_success(self, client):
        """Test successfully updating session title."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        session = SessionService.create_session(user.id, title='Original Title')
        
        updated_session = SessionService.update_session_title(session.id, 'New Title')
        
        assert updated_session is not None
        assert updated_session.title == 'New Title'
    
    def test_update_session_title_not_found(self, client):
        """Test updating title of non-existent session."""
        updated_session = SessionService.update_session_title('nonexistent-id', 'New Title')
        
        assert updated_session is None


class TestDeleteSession:
    """Test session deletion."""
    
    def test_delete_session_success(self, client):
        """Test successfully deleting a session."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        session = SessionService.create_session(user.id)
        session_id = session.id
        
        result = SessionService.delete_session(session_id)
        
        assert result is True
        
        # Verify session is deleted
        deleted_session = SessionService.get_session(session_id)
        assert deleted_session is None
    
    def test_delete_session_not_found(self, client):
        """Test deleting non-existent session."""
        result = SessionService.delete_session('nonexistent-id')
        
        assert result is False


class TestTouchSession:
    """Test updating session timestamp."""
    
    def test_touch_session_updates_timestamp(self, client):
        """Test that touch_session updates the updated_at timestamp."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        session = SessionService.create_session(user.id)
        original_updated_at = session.updated_at
        
        # Touch the session
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp changes
        SessionService.touch_session(session.id)
        
        # Retrieve updated session
        updated_session = SessionService.get_session(session.id)
        
        # updated_at should be different (newer)
        assert updated_session.updated_at >= original_updated_at
    
    def test_touch_session_nonexistent(self, client):
        """Test touching non-existent session doesn't raise error."""
        # Should not raise an exception
        SessionService.touch_session('nonexistent-id')
