"""Tests for Message model."""
import pytest
from datetime import datetime
from app.models import Message, MessageRole
from app.services.message_parser import MessageParser


class TestMessageModel:
    """Test suite for Message model."""
    
    def test_message_model_fields(self):
        """Test that Message model has all required fields."""
        # Create a message instance (not persisted)
        content = [{"type": "text", "text": "Test message"}]
        raw_text = MessageParser.extract_raw_text(content)
        
        message = Message(
            session_id="test-session-id",
            role=MessageRole.USER,
            content=content,
            raw_text=raw_text,
            interrupted=False
        )
        
        # Verify fields
        assert message.session_id == "test-session-id"
        assert message.role == MessageRole.USER
        assert message.content == content
        assert message.raw_text == "Test message"
        assert message.interrupted is False
        # Note: id is generated when added to session, not on instantiation
    
    def test_message_to_dict(self):
        """Test Message to_dict method."""
        content = [{"type": "text", "text": "Hello"}]
        message = Message(
            session_id="session-123",
            role=MessageRole.ASSISTANT,
            content=content,
            raw_text="Hello",
            interrupted=False
        )
        message.created_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = message.to_dict()
        
        assert result['session_id'] == "session-123"
        assert result['role'] == 'assistant'
        assert result['content'] == content
        assert result['raw_text'] == "Hello"
        assert result['interrupted'] is False
        assert 'created_at' in result
    
    def test_message_with_multimodal_content(self):
        """Test Message model with multimodal content."""
        content = [
            {"type": "text", "text": "Check this image:"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}
        ]
        raw_text = MessageParser.extract_raw_text(content)
        
        message = Message(
            session_id="session-456",
            role=MessageRole.USER,
            content=content,
            raw_text=raw_text,
            interrupted=False
        )
        
        assert len(message.content) == 2
        assert message.content[0]["type"] == "text"
        assert message.content[1]["type"] == "image_url"
        assert message.raw_text == "Check this image:"
    
    def test_message_interrupted_flag(self):
        """Test Message model with interrupted flag."""
        content = [{"type": "text", "text": "Partial response"}]
        
        message = Message(
            session_id="session-789",
            role=MessageRole.ASSISTANT,
            content=content,
            raw_text="Partial response",
            interrupted=True
        )
        
        assert message.interrupted is True
    
    def test_message_role_enum(self):
        """Test MessageRole enum values."""
        assert MessageRole.USER.value == 'user'
        assert MessageRole.ASSISTANT.value == 'assistant'
        assert MessageRole.SYSTEM.value == 'system'
    
    def test_message_with_parser_integration(self):
        """Test Message model integration with MessageParser."""
        # Parse content
        content_str = '[{"type": "text", "text": "Integration test"}]'
        parsed_content = MessageParser.parse_content(content_str)
        raw_text = MessageParser.extract_raw_text(parsed_content)
        
        # Create message
        message = Message(
            session_id="session-integration",
            role=MessageRole.USER,
            content=parsed_content,
            raw_text=raw_text
        )
        
        assert message.content == parsed_content
        assert message.raw_text == "Integration test"
        
        # Verify pretty print works
        pretty = MessageParser.pretty_print(message.content)
        assert "Integration test" in pretty
