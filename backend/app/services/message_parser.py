"""Message content parser and validator."""
import json
from typing import List, Dict, Any, Union


class ContentBlockType:
    """Valid content block types."""
    TEXT = 'text'
    IMAGE_URL = 'image_url'
    FILE = 'file'
    AUDIO = 'audio'
    
    @classmethod
    def all_types(cls) -> List[str]:
        """Return all valid content block types."""
        return [cls.TEXT, cls.IMAGE_URL, cls.FILE, cls.AUDIO]


class MessageParserError(Exception):
    """Exception raised for message parsing errors."""
    pass


class MessageParser:
    """Parser and validator for message content structures."""
    
    @staticmethod
    def parse_content(content: Union[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Parse message content into a structured Content_Array.
        
        Args:
            content: Either a JSON string or a list of content blocks
            
        Returns:
            List of validated content blocks
            
        Raises:
            MessageParserError: If content is invalid or cannot be parsed
        """
        # Handle string input (JSON)
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError as e:
                raise MessageParserError(f"Invalid JSON content: {str(e)}")
        
        # Ensure content is a list
        if not isinstance(content, list):
            raise MessageParserError("Content must be a list of content blocks")
        
        # Validate each content block
        validated_blocks = []
        for i, block in enumerate(content):
            try:
                validated_block = MessageParser.validate_content_block(block)
                validated_blocks.append(validated_block)
            except MessageParserError as e:
                raise MessageParserError(f"Invalid content block at index {i}: {str(e)}")
        
        return validated_blocks
    
    @staticmethod
    def validate_content_block(block: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single content block structure.
        
        Args:
            block: Content block dictionary
            
        Returns:
            Validated content block
            
        Raises:
            MessageParserError: If block structure is invalid
        """
        if not isinstance(block, dict):
            raise MessageParserError("Content block must be a dictionary")
        
        # Check for required 'type' field
        if 'type' not in block:
            raise MessageParserError("Content block must have a 'type' field")
        
        block_type = block['type']
        
        # Validate type value
        if block_type not in ContentBlockType.all_types():
            raise MessageParserError(
                f"Invalid content block type '{block_type}'. "
                f"Must be one of: {', '.join(ContentBlockType.all_types())}"
            )
        
        # Validate type-specific fields
        if block_type == ContentBlockType.TEXT:
            if 'text' not in block:
                raise MessageParserError("Text content block must have a 'text' field")
            if not isinstance(block['text'], str):
                raise MessageParserError("Text field must be a string")
        
        elif block_type == ContentBlockType.IMAGE_URL:
            if 'image_url' not in block:
                raise MessageParserError("Image content block must have an 'image_url' field")
            if not isinstance(block['image_url'], dict):
                raise MessageParserError("Image_url field must be a dictionary")
            if 'url' not in block['image_url']:
                raise MessageParserError("Image_url must contain a 'url' field")
            if not isinstance(block['image_url']['url'], str):
                raise MessageParserError("Image URL must be a string")
        
        elif block_type == ContentBlockType.FILE:
            if 'file' not in block:
                raise MessageParserError("File content block must have a 'file' field")
            if not isinstance(block['file'], dict):
                raise MessageParserError("File field must be a dictionary")
            if 'url' not in block['file']:
                raise MessageParserError("File must contain a 'url' field")
            if 'name' not in block['file']:
                raise MessageParserError("File must contain a 'name' field")
            if not isinstance(block['file']['url'], str):
                raise MessageParserError("File URL must be a string")
            if not isinstance(block['file']['name'], str):
                raise MessageParserError("File name must be a string")
        
        elif block_type == ContentBlockType.AUDIO:
            if 'audio' not in block:
                raise MessageParserError("Audio content block must have an 'audio' field")
            if not isinstance(block['audio'], dict):
                raise MessageParserError("Audio field must be a dictionary")
            if 'url' not in block['audio']:
                raise MessageParserError("Audio must contain a 'url' field")
            if not isinstance(block['audio']['url'], str):
                raise MessageParserError("Audio URL must be a string")
        
        return block
    
    @staticmethod
    def extract_raw_text(content: List[Dict[str, Any]]) -> str:
        """
        Extract plain text from content blocks for search and display.
        
        Args:
            content: List of content blocks
            
        Returns:
            Concatenated text from all text blocks
        """
        text_parts = []
        
        for block in content:
            if block.get('type') == ContentBlockType.TEXT:
                text = block.get('text', '')
                if text:
                    text_parts.append(text)
        
        return ' '.join(text_parts)
    
    @staticmethod
    def pretty_print(content: List[Dict[str, Any]], indent: int = 2) -> str:
        """
        Format content blocks as pretty-printed JSON for debugging.
        
        Args:
            content: List of content blocks
            indent: Number of spaces for indentation
            
        Returns:
            Pretty-printed JSON string
        """
        return json.dumps(content, indent=indent, ensure_ascii=False)
