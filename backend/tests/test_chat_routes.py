"""Tests for chat routes."""
import pytest
import json
from unittest.mock import patch, Mock
from app.models import db, User, Session, Message


class TestChatCompletions:
    """Test cases for chat completions endpoint."""
    
    def test_chat_completions_requires_auth(self, client):
        """Test that chat completions endpoint requires authentication."""
        response = client.post('/api/chat/completions', json={})
        assert response.status_code == 401
    
    def test_chat_completions_missing_session_id(self, client, auth_headers):
        """Test error when session_id is missing."""
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={'messages': [{'role': 'user', 'content': 'Hello'}]}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'session_id' in data['error']
    
    def test_chat_completions_missing_messages(self, client, auth_headers):
        """Test error when messages array is missing."""
        # Create session
        user = User.query.filter_by(username='testuser').first()
        session = Session(user_id=user.id, title='Test')
        db.session.add(session)
        db.session.commit()
        
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={'session_id': session.id}
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'messages' in data['error']
    
    def test_chat_completions_invalid_session(self, client, auth_headers):
        """Test error when session doesn't exist or doesn't belong to user."""
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={
                'session_id': 'invalid-session-id',
                'messages': [{'role': 'user', 'content': 'Hello'}]
            }
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'not found' in data['error'].lower() or 'access denied' in data['error'].lower()
    
    def test_chat_completions_last_message_not_user(self, client, auth_headers):
        """Test error when last message is not from user."""
        user = User.query.filter_by(username='testuser').first()
        session = Session(user_id=user.id, title='Test')
        db.session.add(session)
        db.session.commit()
        
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={
                'session_id': session.id,
                'messages': [{'role': 'assistant', 'content': 'Hello'}]
            }
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'user' in data['error'].lower()
    
    @patch('app.routes.chat.StreamService')
    def test_chat_completions_success(self, mock_stream_service_class, client, auth_headers):
        """Test successful chat completion with streaming."""
        # Create session
        user = User.query.filter_by(username='testuser').first()
        session = Session(user_id=user.id, title='Test')
        db.session.add(session)
        db.session.commit()
        
        # Mock stream service
        mock_stream_service = Mock()
        mock_stream_chunks = [
            'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
            'data: {"choices": [{"delta": {"content": " there"}}]}\n\n',
            'data: [DONE]\n\n'
        ]
        mock_stream_service.create_stream.return_value = iter(mock_stream_chunks)
        mock_stream_service_class.return_value = mock_stream_service
        
        # Send request
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={
                'session_id': session.id,
                'messages': [{'role': 'user', 'content': 'Hi'}],
                'stream': True
            }
        )
        
        assert response.status_code == 200
        assert response.content_type == 'text/event-stream; charset=utf-8'
        
        # Verify user message was persisted
        messages = Message.query.filter_by(session_id=session.id).all()
        assert len(messages) >= 1
        assert messages[0].role.value == 'user'
        assert messages[0].raw_text == 'Hi'
    
    @patch('app.routes.chat.StreamService')
    def test_chat_completions_persists_assistant_response(self, mock_stream_service_class, client, auth_headers):
        """Test that assistant response is persisted after streaming."""
        # Create session
        user = User.query.filter_by(username='testuser').first()
        session = Session(user_id=user.id, title='Test')
        db.session.add(session)
        db.session.commit()
        
        # Mock stream service
        mock_stream_service = Mock()
        mock_stream_chunks = [
            'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n',
            'data: {"choices": [{"delta": {"content": " world"}}]}\n\n',
            'data: [DONE]\n\n'
        ]
        mock_stream_service.create_stream.return_value = iter(mock_stream_chunks)
        mock_stream_service_class.return_value = mock_stream_service
        
        # Send request
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={
                'session_id': session.id,
                'messages': [{'role': 'user', 'content': 'Hi'}],
                'stream': True
            }
        )
        
        # Consume the stream
        data = b''.join(response.iter_encoded())
        
        # Verify both user and assistant messages were persisted
        messages = Message.query.filter_by(session_id=session.id).order_by(Message.created_at).all()
        assert len(messages) == 2
        assert messages[0].role.value == 'user'
        assert messages[1].role.value == 'assistant'
        assert 'Hello world' in messages[1].raw_text
    
    @patch('app.routes.chat.ContextManager')
    @patch('app.routes.chat.StreamService')
    def test_chat_completions_applies_context_truncation(self, mock_stream_service_class, mock_context_manager_class, client, auth_headers):
        """Test that context truncation is applied before streaming."""
        # Create session with existing messages
        user = User.query.filter_by(username='testuser').first()
        session = Session(user_id=user.id, title='Test')
        db.session.add(session)
        db.session.commit()
        
        # Add some existing messages
        from app.services.message_service import MessageService
        MessageService.create_message(session.id, 'user', 'Previous message 1')
        MessageService.create_message(session.id, 'assistant', 'Previous response 1')
        
        # Mock context manager
        mock_context_manager = Mock()
        mock_context_manager.prepare_context.return_value = [
            {'role': 'user', 'content': 'Previous message 1'},
            {'role': 'assistant', 'content': 'Previous response 1'},
            {'role': 'user', 'content': 'New message'}
        ]
        mock_context_manager_class.return_value = mock_context_manager
        
        # Mock stream service
        mock_stream_service = Mock()
        mock_stream_service.create_stream.return_value = iter(['data: [DONE]\n\n'])
        mock_stream_service_class.return_value = mock_stream_service
        
        # Send request
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={
                'session_id': session.id,
                'messages': [{'role': 'user', 'content': 'New message'}],
                'stream': True
            }
        )
        
        # Verify context manager was called
        mock_context_manager.prepare_context.assert_called_once()
        
        # Verify stream service received prepared context
        mock_stream_service.create_stream.assert_called_once()
    
    @patch('app.routes.chat.StreamService')
    def test_chat_completions_with_model_config(self, mock_stream_service_class, client, auth_headers):
        """Test that custom model configuration is passed to stream service."""
        user = User.query.filter_by(username='testuser').first()
        session = Session(user_id=user.id, title='Test')
        db.session.add(session)
        db.session.commit()
        
        # Mock stream service
        mock_stream_service = Mock()
        mock_stream_service.create_stream.return_value = iter(['data: [DONE]\n\n'])
        mock_stream_service_class.return_value = mock_stream_service
        
        # Send request with custom config
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={
                'session_id': session.id,
                'messages': [{'role': 'user', 'content': 'Test'}],
                'stream': True,
                'model': 'custom-model',
                'temperature': 0.8,
                'max_tokens': 2000
            }
        )
        
        # Verify stream service was called with model config
        call_args = mock_stream_service.create_stream.call_args
        model_config = call_args[1]['model_config']
        assert model_config['model'] == 'custom-model'
        assert model_config['temperature'] == 0.8
        assert model_config['max_tokens'] == 2000
    
    def test_chat_completions_non_streaming_not_implemented(self, client, auth_headers):
        """Test that non-streaming mode returns not implemented."""
        user = User.query.filter_by(username='testuser').first()
        session = Session(user_id=user.id, title='Test')
        db.session.add(session)
        db.session.commit()
        
        response = client.post(
            '/api/chat/completions',
            headers=auth_headers,
            json={
                'session_id': session.id,
                'messages': [{'role': 'user', 'content': 'Test'}],
                'stream': False
            }
        )
        
        assert response.status_code == 501
