"""Context manager for token counting and truncation."""
import logging
from typing import List, Dict, Any
import tiktoken
from config import Config


logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages conversation context length to prevent exceeding LLM token limits.
    
    Implements Requirements 6.1, 6.2, 6.3, 6.4:
    - Calculates token counts for messages
    - Truncates context when exceeding 80% of limit
    - Preserves most recent 10 messages
    - Always includes system prompt
    """
    
    # Token limit threshold (80% of context limit)
    TRUNCATION_THRESHOLD = 0.8
    
    # Number of recent messages to preserve during truncation
    RECENT_MESSAGE_COUNT = 10
    
    def __init__(self, context_limit: int = None, model: str = None):
        """
        Initialize the context manager.
        
        Args:
            context_limit: Maximum token limit (defaults to Config.LLM_CONTEXT_LIMIT)
            model: Model name for tokenizer (defaults to Config.LLM_MODEL)
        """
        self.context_limit = context_limit or Config.LLM_CONTEXT_LIMIT
        self.model = model or Config.LLM_MODEL
        
        # Initialize tokenizer
        # Use cl100k_base encoding which works for most modern models
        try:
            self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except KeyError:
            # Fallback to cl100k_base if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def calculate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        Calculate the total token count for a list of messages.
        
        Implements Requirement 6.1: Calculate token count of conversation history.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' fields
            
        Returns:
            Total token count for all messages
        """
        total_tokens = 0
        
        for message in messages:
            # Count tokens for role
            role = message.get('role', '')
            total_tokens += len(self.encoding.encode(role))
            
            # Count tokens for content
            content = message.get('content', '')
            
            # Handle content as string or list of content blocks
            if isinstance(content, str):
                total_tokens += len(self.encoding.encode(content))
            elif isinstance(content, list):
                # Extract text from content blocks
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text = block.get('text', '')
                        total_tokens += len(self.encoding.encode(text))
            
            # Add overhead tokens for message formatting (approximately 4 tokens per message)
            total_tokens += 4
        
        # Add overhead for chat completion formatting (approximately 3 tokens)
        total_tokens += 3
        
        return total_tokens
    
    def truncate_context(
        self, 
        messages: List[Dict[str, Any]], 
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Truncate context when exceeding token limit threshold.
        
        Implements Requirements 6.2, 6.3:
        - Truncates older messages while preserving recent 10 messages
        - Always includes system prompt regardless of truncation
        
        Args:
            messages: List of message dictionaries
            limit: Token limit (defaults to self.context_limit)
            
        Returns:
            Truncated list of messages
        """
        if limit is None:
            limit = self.context_limit
        
        # Calculate current token count
        current_tokens = self.calculate_tokens(messages)
        threshold = int(limit * self.TRUNCATION_THRESHOLD)
        
        # If under threshold, no truncation needed
        if current_tokens <= threshold:
            return messages
        
        # Log truncation event (Requirement 6.4)
        logger.info(
            f"Context truncation triggered: {current_tokens} tokens exceeds "
            f"threshold of {threshold} (80% of {limit})"
        )
        
        # Separate system prompt from other messages
        system_messages = [msg for msg in messages if msg.get('role') == 'system']
        non_system_messages = [msg for msg in messages if msg.get('role') != 'system']
        
        # Always preserve system prompt (Requirement 6.3)
        truncated_messages = system_messages.copy()
        
        # Preserve most recent N messages (Requirement 6.2)
        recent_messages = non_system_messages[-self.RECENT_MESSAGE_COUNT:]
        truncated_messages.extend(recent_messages)
        
        # Calculate tokens after truncation
        final_tokens = self.calculate_tokens(truncated_messages)
        messages_removed = len(non_system_messages) - len(recent_messages)
        
        # Log truncation details (Requirement 6.4)
        logger.info(
            f"Context truncated: removed {messages_removed} older messages, "
            f"preserved {len(system_messages)} system messages and "
            f"{len(recent_messages)} recent messages. "
            f"Token count reduced from {current_tokens} to {final_tokens}"
        )
        
        return truncated_messages
    
    def prepare_context(
        self, 
        messages: List[Dict[str, Any]], 
        session_id: str = None
    ) -> List[Dict[str, Any]]:
        """
        Prepare conversation context with automatic truncation if needed.
        
        This is the main method to use when preparing context for LLM requests.
        
        Args:
            messages: List of message dictionaries
            session_id: Optional session ID for logging
            
        Returns:
            Prepared (and possibly truncated) list of messages
        """
        if session_id:
            logger.debug(f"Preparing context for session {session_id}")
        
        # Truncate if necessary
        prepared_messages = self.truncate_context(messages)
        
        return prepared_messages
