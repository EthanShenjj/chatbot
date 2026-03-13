"""Tests for stream service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from app.services.stream_service import StreamService


class TestStreamService:
    """Test cases for StreamService."""
    
    def test_init_with_defaults(self):
        """Test initialization with default configuration."""
        service = StreamService()
        
        assert service.api_key is not None
        assert service.endpoint is not None
        assert service.model is not None
        assert service.temperature is not None
        assert service.max_tokens is not None
        assert service.top_p is not None
    
    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        service = StreamService(
            api_key='test-key',
            endpoint='https://test.com/api',
            model='test-model',
            temperature=0.5,
            max_tokens=2000,
            top_p=0.9
        )
        
        assert service.api_key == 'test-key'
        assert service.endpoint == 'https://test.com/api'
        assert service.model == 'test-model'
        assert service.temperature == 0.5
        assert service.max_tokens == 2000
        assert service.top_p == 0.9
    
    @patch('app.services.stream_service.requests.post')
    def test_create_stream_success(self, mock_post):
        """Test successful stream creation and token forwarding."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        
        # Simulate SSE stream with multiple chunks
        mock_lines = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            b'data: {"choices": [{"delta": {"content": " world"}}]}',
            b'data: {"choices": [{"delta": {"content": "!"}}]}',
            b'data: [DONE]'
        ]
        mock_response.iter_lines = Mock(return_value=mock_lines)
        mock_post.return_value = mock_response
        
        service = StreamService(api_key='test-key')
        messages = [{'role': 'user', 'content': 'Hello'}]
        
        # Collect streamed chunks
        chunks = []
        for chunk in service.create_stream(messages):
            chunks.append(chunk)
        
        # Verify chunks were forwarded
        assert len(chunks) == 4
        assert chunks[0] == 'data: {"choices": [{"delta": {"content": "Hello"}}]}\n\n'
        assert chunks[1] == 'data: {"choices": [{"delta": {"content": " world"}}]}\n\n'
        assert chunks[2] == 'data: {"choices": [{"delta": {"content": "!"}}]}\n\n'
        assert chunks[3] == 'data: [DONE]\n\n'
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == service.endpoint
        assert 'Authorization' in call_args[1]['headers']
        assert call_args[1]['json']['messages'] == messages
        assert call_args[1]['json']['stream'] is True
    
    @patch('app.services.stream_service.requests.post')
    def test_create_stream_with_model_config(self, mock_post):
        """Test stream creation with custom model configuration."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.iter_lines = Mock(return_value=[b'data: [DONE]'])
        mock_post.return_value = mock_response
        
        service = StreamService(api_key='test-key')
        messages = [{'role': 'user', 'content': 'Test'}]
        model_config = {
            'model': 'custom-model',
            'temperature': 0.8,
            'max_tokens': 1000
        }
        
        list(service.create_stream(messages, model_config))
        
        # Verify custom config was used
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['model'] == 'custom-model'
        assert payload['temperature'] == 0.8
        assert payload['max_tokens'] == 1000
    
    @patch('app.services.stream_service.requests.post')
    def test_create_stream_timeout_error(self, mock_post):
        """Test handling of timeout errors."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        service = StreamService(api_key='test-key')
        messages = [{'role': 'user', 'content': 'Test'}]
        
        with pytest.raises(requests.exceptions.Timeout):
            chunks = list(service.create_stream(messages))
    
    @patch('app.services.stream_service.requests.post')
    def test_create_stream_connection_error(self, mock_post):
        """Test handling of connection errors."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Cannot connect")
        
        service = StreamService(api_key='test-key')
        messages = [{'role': 'user', 'content': 'Test'}]
        
        with pytest.raises(requests.exceptions.ConnectionError):
            chunks = list(service.create_stream(messages))
    
    @patch('app.services.stream_service.requests.post')
    def test_create_stream_http_error(self, mock_post):
        """Test handling of HTTP errors."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server error")
        mock_post.return_value = mock_response
        
        service = StreamService(api_key='test-key')
        messages = [{'role': 'user', 'content': 'Test'}]
        
        with pytest.raises(requests.exceptions.HTTPError):
            chunks = list(service.create_stream(messages))
    
    @patch('app.services.stream_service.requests.post')
    def test_create_stream_accumulates_response(self, mock_post):
        """Test that stream accumulates complete response text."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        
        mock_lines = [
            b'data: {"choices": [{"delta": {"content": "Hello"}}]}',
            b'data: {"choices": [{"delta": {"content": " world"}}]}',
            b'data: [DONE]'
        ]
        mock_response.iter_lines = Mock(return_value=mock_lines)
        mock_post.return_value = mock_response
        
        service = StreamService(api_key='test-key')
        messages = [{'role': 'user', 'content': 'Test'}]
        
        # Consume the generator to get the return value
        gen = service.create_stream(messages)
        chunks = []
        try:
            while True:
                chunks.append(next(gen))
        except StopIteration as e:
            full_response = e.value
        
        # Verify accumulated response
        assert full_response == "Hello world"
    
    @patch('app.services.stream_service.requests.post')
    def test_create_stream_handles_malformed_chunks(self, mock_post):
        """Test that stream handles malformed JSON chunks gracefully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        
        mock_lines = [
            b'data: {"choices": [{"delta": {"content": "Good"}}]}',
            b'data: {invalid json}',  # Malformed chunk
            b'data: {"choices": [{"delta": {"content": " data"}}]}',
            b'data: [DONE]'
        ]
        mock_response.iter_lines = Mock(return_value=mock_lines)
        mock_post.return_value = mock_response
        
        service = StreamService(api_key='test-key')
        messages = [{'role': 'user', 'content': 'Test'}]
        
        # Should not raise exception, just skip malformed chunk
        chunks = list(service.create_stream(messages))
        
        # Verify we got all chunks including malformed one (forwarded as-is)
        assert len(chunks) == 4
        assert 'Good' in chunks[0]
        assert 'invalid json' in chunks[1]
        assert 'data' in chunks[2]
