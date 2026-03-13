"""Integration tests for session routes."""
import pytest
import json
from app.models import db, User, Session, Message, MessageRole
from app.services import AuthService


class TestGetSessions:
    """Test GET /api/sessions endpoint."""
    
    def test_get_sessions_success(self, client):
        """Test successfully retrieving user sessions."""
        # Create user and get token
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        # Create some sessions
        session1 = Session(user_id=user.id, title='Session 1')
        session2 = Session(user_id=user.id, title='Session 2')
        db.session.add_all([session1, session2])
        db.session.commit()
        
        # Get sessions
        response = client.get(
            '/api/sessions',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'sessions' in data
        assert len(data['sessions']) == 2
        
        # Verify session structure
        for session in data['sessions']:
            assert 'id' in session
            assert 'title' in session
            assert 'updated_at' in session
    
    def test_get_sessions_ordered_by_updated_at(self, client):
        """Test that sessions are ordered by most recent update."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        # Create sessions
        session1 = Session(user_id=user.id, title='First')
        session2 = Session(user_id=user.id, title='Second')
        db.session.add_all([session1, session2])
        db.session.commit()
        
        # Update session1 to make it most recent
        from datetime import datetime
        session1.updated_at = datetime.utcnow()
        db.session.commit()
        
        response = client.get(
            '/api/sessions',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.get_json()
        sessions = data['sessions']
        
        # First session should be the most recently updated
        assert sessions[0]['title'] == 'First'
    
    def test_get_sessions_empty(self, client):
        """Test getting sessions when user has none."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        response = client.get(
            '/api/sessions',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['sessions'] == []
    
    def test_get_sessions_unauthorized(self, client):
        """Test getting sessions without authentication."""
        response = client.get('/api/sessions')
        
        assert response.status_code == 401
    
    def test_get_sessions_only_returns_user_sessions(self, client):
        """Test that only the authenticated user's sessions are returned."""
        # Create two users
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
        session1 = Session(user_id=user1.id, title='User1 Session')
        session2 = Session(user_id=user2.id, title='User2 Session')
        db.session.add_all([session1, session2])
        db.session.commit()
        
        # Get user1's token and sessions
        token = AuthService.generate_token(user1.id, user1.username)
        response = client.get(
            '/api/sessions',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.get_json()
        assert len(data['sessions']) == 1
        assert data['sessions'][0]['title'] == 'User1 Session'


class TestCreateSession:
    """Test POST /api/sessions endpoint."""
    
    def test_create_session_success(self, client):
        """Test successfully creating a new session."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        response = client.post(
            '/api/sessions',
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'session_id' in data
        assert 'created_at' in data
        assert data['session_id'] is not None
        
        # Verify session was created in database
        session = Session.query.get(data['session_id'])
        assert session is not None
        assert session.user_id == user.id
    
    def test_create_session_with_title(self, client):
        """Test creating session with custom title."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        response = client.post(
            '/api/sessions',
            data=json.dumps({'title': 'My Custom Session'}),
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        # Verify title was set
        session = Session.query.get(data['session_id'])
        assert session.title == 'My Custom Session'
    
    def test_create_session_unauthorized(self, client):
        """Test creating session without authentication."""
        response = client.post(
            '/api/sessions',
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_create_session_generates_unique_ids(self, client):
        """Test that each created session gets a unique ID."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        # Create two sessions
        response1 = client.post(
            '/api/sessions',
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        response2 = client.post(
            '/api/sessions',
            headers={'Authorization': f'Bearer {token}'},
            content_type='application/json'
        )
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        assert data1['session_id'] != data2['session_id']


class TestGetSessionMessages:
    """Test GET /api/sessions/<session_id>/messages endpoint."""
    
    def test_get_session_messages_success(self, client):
        """Test successfully retrieving messages for a session."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        # Create session and messages
        session = Session(user_id=user.id, title='Test Session')
        db.session.add(session)
        db.session.commit()
        
        message1 = Message(
            session_id=session.id,
            role=MessageRole.USER,
            content=[{'type': 'text', 'text': 'Hello'}],
            raw_text='Hello'
        )
        message2 = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=[{'type': 'text', 'text': 'Hi there!'}],
            raw_text='Hi there!'
        )
        db.session.add_all([message1, message2])
        db.session.commit()
        
        response = client.get(
            f'/api/sessions/{session.id}/messages',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'messages' in data
        assert len(data['messages']) == 2
        
        # Verify message structure
        for message in data['messages']:
            assert 'id' in message
            assert 'role' in message
            assert 'content' in message
            assert 'raw_text' in message
            assert 'created_at' in message
            assert 'interrupted' in message
    
    def test_get_session_messages_ordered_by_created_at(self, client):
        """Test that messages are ordered by creation time ascending."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        session = Session(user_id=user.id)
        db.session.add(session)
        db.session.commit()
        
        # Create messages in specific order
        message1 = Message(
            session_id=session.id,
            role=MessageRole.USER,
            content=[{'type': 'text', 'text': 'First'}],
            raw_text='First'
        )
        message2 = Message(
            session_id=session.id,
            role=MessageRole.ASSISTANT,
            content=[{'type': 'text', 'text': 'Second'}],
            raw_text='Second'
        )
        db.session.add_all([message1, message2])
        db.session.commit()
        
        response = client.get(
            f'/api/sessions/{session.id}/messages',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        data = response.get_json()
        messages = data['messages']
        
        assert messages[0]['raw_text'] == 'First'
        assert messages[1]['raw_text'] == 'Second'
    
    def test_get_session_messages_empty(self, client):
        """Test getting messages for session with no messages."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        session = Session(user_id=user.id)
        db.session.add(session)
        db.session.commit()
        
        response = client.get(
            f'/api/sessions/{session.id}/messages',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['messages'] == []
    
    def test_get_session_messages_unauthorized(self, client):
        """Test getting messages without authentication."""
        response = client.get('/api/sessions/some-id/messages')
        
        assert response.status_code == 401
    
    def test_get_session_messages_wrong_user(self, client):
        """Test getting messages for session owned by different user."""
        # Create two users
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
        
        # Create session for user1
        session = Session(user_id=user1.id)
        db.session.add(session)
        db.session.commit()
        
        # Try to access with user2's token
        token = AuthService.generate_token(user2.id, user2.username)
        response = client.get(
            f'/api/sessions/{session.id}/messages',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['code'] == 'SESSION_NOT_FOUND'
    
    def test_get_session_messages_nonexistent_session(self, client):
        """Test getting messages for non-existent session."""
        user = User(
            username='testuser',
            password_hash=AuthService.hash_password('password')
        )
        db.session.add(user)
        db.session.commit()
        
        token = AuthService.generate_token(user.id, user.username)
        
        response = client.get(
            '/api/sessions/nonexistent-id/messages',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert data['code'] == 'SESSION_NOT_FOUND'
