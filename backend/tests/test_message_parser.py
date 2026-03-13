"""Tests for message parser."""
import pytest
import json
from app.services.message_parser import MessageParser, MessageParserError, ContentBlockType


class TestMessageParser:
    """Test suite for MessageParser."""
    
    def test_parse_text_content_block(self):
        """Test parsing a simple text content block."""
        content = [{"type": "text", "text": "Hello, world!"}]
        result = MessageParser.parse_content(content)
        
        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert result[0]["text"] == "Hello, world!"
    
    def test_parse_json_string_content(self):
        """Test parsing content from JSON string."""
        content_str = json.dumps([{"type": "text", "text": "Test message"}])
        result = MessageParser.parse_content(content_str)
        
        assert len(result) == 1
        assert result[0]["type"] == "text"
        assert result[0]["text"] == "Test message"
    
    def test_parse_image_url_content_block(self):
        """Test parsing an image_url content block."""
        content = [
            {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}}
        ]
        result = MessageParser.parse_content(content)
        
        assert len(result) == 1
        assert result[0]["type"] == "image_url"
        assert result[0]["image_url"]["url"] == "https://example.com/image.png"
    
    def test_parse_file_content_block(self):
        """Test parsing a file content block."""
        content = [
            {
                "type": "file",
                "file": {"url": "https://example.com/doc.pdf", "name": "document.pdf"}
            }
        ]
        result = MessageParser.parse_content(content)
        
        assert len(result) == 1
        assert result[0]["type"] == "file"
        assert result[0]["file"]["url"] == "https://example.com/doc.pdf"
        assert result[0]["file"]["name"] == "document.pdf"
    
    def test_parse_audio_content_block(self):
        """Test parsing an audio content block."""
        content = [
            {"type": "audio", "audio": {"url": "https://example.com/audio.mp3"}}
        ]
        result = MessageParser.parse_content(content)
        
        assert len(result) == 1
        assert result[0]["type"] == "audio"
        assert result[0]["audio"]["url"] == "https://example.com/audio.mp3"
    
    def test_parse_multimodal_content(self):
        """Test parsing content with multiple block types."""
        content = [
            {"type": "text", "text": "Check out this image:"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}},
            {"type": "text", "text": "And this document:"},
            {"type": "file", "file": {"url": "https://example.com/doc.pdf", "name": "report.pdf"}}
        ]
        result = MessageParser.parse_content(content)
        
        assert len(result) == 4
        assert result[0]["type"] == "text"
        assert result[1]["type"] == "image_url"
        assert result[2]["type"] == "text"
        assert result[3]["type"] == "file"
    
    def test_parse_invalid_json_string(self):
        """Test that invalid JSON raises MessageParserError."""
        with pytest.raises(MessageParserError, match="Invalid JSON content"):
            MessageParser.parse_content("{invalid json")
    
    def test_parse_non_list_content(self):
        """Test that non-list content raises MessageParserError."""
        with pytest.raises(MessageParserError, match="Content must be a list"):
            MessageParser.parse_content({"type": "text", "text": "Not a list"})
    
    def test_validate_missing_type_field(self):
        """Test that content block without type field raises error."""
        content = [{"text": "Missing type field"}]
        with pytest.raises(MessageParserError, match="must have a 'type' field"):
            MessageParser.parse_content(content)
    
    def test_validate_invalid_type_value(self):
        """Test that invalid type value raises error."""
        content = [{"type": "invalid_type", "text": "Test"}]
        with pytest.raises(MessageParserError, match="Invalid content block type"):
            MessageParser.parse_content(content)
    
    def test_validate_text_block_missing_text_field(self):
        """Test that text block without text field raises error."""
        content = [{"type": "text"}]
        with pytest.raises(MessageParserError, match="must have a 'text' field"):
            MessageParser.parse_content(content)
    
    def test_validate_text_block_non_string_text(self):
        """Test that text block with non-string text raises error."""
        content = [{"type": "text", "text": 123}]
        with pytest.raises(MessageParserError, match="Text field must be a string"):
            MessageParser.parse_content(content)
    
    def test_validate_image_block_missing_image_url_field(self):
        """Test that image block without image_url field raises error."""
        content = [{"type": "image_url"}]
        with pytest.raises(MessageParserError, match="must have an 'image_url' field"):
            MessageParser.parse_content(content)
    
    def test_validate_image_block_missing_url(self):
        """Test that image block without url raises error."""
        content = [{"type": "image_url", "image_url": {}}]
        with pytest.raises(MessageParserError, match="must contain a 'url' field"):
            MessageParser.parse_content(content)
    
    def test_validate_file_block_missing_file_field(self):
        """Test that file block without file field raises error."""
        content = [{"type": "file"}]
        with pytest.raises(MessageParserError, match="must have a 'file' field"):
            MessageParser.parse_content(content)
    
    def test_validate_file_block_missing_url(self):
        """Test that file block without url raises error."""
        content = [{"type": "file", "file": {"name": "test.pdf"}}]
        with pytest.raises(MessageParserError, match="must contain a 'url' field"):
            MessageParser.parse_content(content)
    
    def test_validate_file_block_missing_name(self):
        """Test that file block without name raises error."""
        content = [{"type": "file", "file": {"url": "https://example.com/file.pdf"}}]
        with pytest.raises(MessageParserError, match="must contain a 'name' field"):
            MessageParser.parse_content(content)
    
    def test_validate_audio_block_missing_audio_field(self):
        """Test that audio block without audio field raises error."""
        content = [{"type": "audio"}]
        with pytest.raises(MessageParserError, match="must have an 'audio' field"):
            MessageParser.parse_content(content)
    
    def test_validate_audio_block_missing_url(self):
        """Test that audio block without url raises error."""
        content = [{"type": "audio", "audio": {}}]
        with pytest.raises(MessageParserError, match="must contain a 'url' field"):
            MessageParser.parse_content(content)
    
    def test_extract_raw_text_single_text_block(self):
        """Test extracting raw text from single text block."""
        content = [{"type": "text", "text": "Hello, world!"}]
        raw_text = MessageParser.extract_raw_text(content)
        
        assert raw_text == "Hello, world!"
    
    def test_extract_raw_text_multiple_text_blocks(self):
        """Test extracting raw text from multiple text blocks."""
        content = [
            {"type": "text", "text": "First part."},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}},
            {"type": "text", "text": "Second part."}
        ]
        raw_text = MessageParser.extract_raw_text(content)
        
        assert raw_text == "First part. Second part."
    
    def test_extract_raw_text_no_text_blocks(self):
        """Test extracting raw text when no text blocks present."""
        content = [
            {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}
        ]
        raw_text = MessageParser.extract_raw_text(content)
        
        assert raw_text == ""
    
    def test_extract_raw_text_empty_content(self):
        """Test extracting raw text from empty content."""
        content = []
        raw_text = MessageParser.extract_raw_text(content)
        
        assert raw_text == ""
    
    def test_pretty_print_single_block(self):
        """Test pretty printing a single content block."""
        content = [{"type": "text", "text": "Test"}]
        result = MessageParser.pretty_print(content)
        
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == content
        
        # Verify it's formatted (contains newlines)
        assert '\n' in result
    
    def test_pretty_print_multimodal_content(self):
        """Test pretty printing multimodal content."""
        content = [
            {"type": "text", "text": "Hello"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.jpg"}}
        ]
        result = MessageParser.pretty_print(content)
        
        # Verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == content
        
        # Verify it's formatted
        assert '\n' in result
    
    def test_pretty_print_custom_indent(self):
        """Test pretty printing with custom indentation."""
        content = [{"type": "text", "text": "Test"}]
        result = MessageParser.pretty_print(content, indent=4)
        
        # Verify custom indentation is used
        assert '    ' in result  # 4 spaces
    
    def test_content_block_type_constants(self):
        """Test ContentBlockType constants."""
        assert ContentBlockType.TEXT == 'text'
        assert ContentBlockType.IMAGE_URL == 'image_url'
        assert ContentBlockType.FILE == 'file'
        assert ContentBlockType.AUDIO == 'audio'
        
        all_types = ContentBlockType.all_types()
        assert len(all_types) == 4
        assert 'text' in all_types
        assert 'image_url' in all_types
        assert 'file' in all_types
        assert 'audio' in all_types
