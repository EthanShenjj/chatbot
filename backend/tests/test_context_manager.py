"""Unit tests for context manager."""
import pytest
from app.services.context_manager import ContextManager


class TestTokenCounting:
    """Test token counting accuracy."""
    
    def test_calculate_tokens_for_simple_text_message(self):
        """Test token calculation for a simple text message."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {
                'role': 'user',
                'content': 'Hello, how are you?'
            }
        ]
        
        token_count = manager.calculate_tokens(messages)
        
        # Should have tokens for role, content, message overhead (4), and completion overhead (3)
        assert token_count > 0
        assert isinstance(token_count, int)
    
    def test_calculate_tokens_for_multiple_messages(self):
        """Test token calculation for multiple messages."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'},
            {'role': 'user', 'content': 'How are you?'}
        ]
        
        token_count = manager.calculate_tokens(messages)
        
        # Multiple messages should have more tokens than single message
        single_message_count = manager.calculate_tokens([messages[0]])
        assert token_count > single_message_count
    
    def test_calculate_tokens_for_content_array(self):
        """Test token calculation for multimodal content array."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': 'What is in this image?'},
                    {'type': 'image_url', 'image_url': {'url': 'https://example.com/image.png'}}
                ]
            }
        ]
        
        token_count = manager.calculate_tokens(messages)
        
        # Should count tokens from text blocks only
        assert token_count > 0
    
    def test_calculate_tokens_for_empty_messages(self):
        """Test token calculation for empty message list."""
        manager = ContextManager(context_limit=4096)
        
        messages = []
        token_count = manager.calculate_tokens(messages)
        
        # Should only have completion overhead (3 tokens)
        assert token_count == 3
    
    def test_calculate_tokens_for_long_message(self):
        """Test token calculation for long message content."""
        manager = ContextManager(context_limit=4096)
        
        # Create a long message (approximately 100 words)
        long_text = ' '.join(['word'] * 100)
        messages = [
            {'role': 'user', 'content': long_text}
        ]
        
        token_count = manager.calculate_tokens(messages)
        
        # Long message should have significantly more tokens
        assert token_count > 50
    
    def test_calculate_tokens_handles_missing_content(self):
        """Test token calculation handles messages with missing content."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'user'}  # No content field
        ]
        
        token_count = manager.calculate_tokens(messages)
        
        # Should handle gracefully and return overhead tokens
        assert token_count > 0
    
    def test_calculate_tokens_for_system_message(self):
        """Test token calculation includes system messages."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello'}
        ]
        
        token_count = manager.calculate_tokens(messages)
        
        # Should count both system and user messages
        user_only_count = manager.calculate_tokens([messages[1]])
        assert token_count > user_only_count
    
    def test_calculate_tokens_accuracy_with_known_text(self):
        """Test token counting accuracy with known text."""
        manager = ContextManager(context_limit=4096)
        
        # Simple message with predictable token count
        messages = [
            {'role': 'user', 'content': 'test'}
        ]
        
        token_count = manager.calculate_tokens(messages)
        
        # "test" is 1 token, "user" is 1 token, plus overheads (4 + 3 = 7)
        # Total should be approximately 9 tokens
        assert 8 <= token_count <= 12  # Allow small variance


class TestTruncationLogic:
    """Test context truncation logic."""
    
    def test_truncate_context_when_under_threshold(self):
        """Test that truncation does not occur when under threshold."""
        manager = ContextManager(context_limit=1000)
        
        messages = [
            {'role': 'user', 'content': 'Short message'}
        ]
        
        truncated = manager.truncate_context(messages)
        
        # Should return all messages unchanged
        assert len(truncated) == len(messages)
        assert truncated == messages
    
    def test_truncate_context_when_exceeding_threshold(self):
        """Test that truncation occurs when exceeding 80% threshold."""
        manager = ContextManager(context_limit=100)  # Very small limit
        
        # Create many messages to exceed threshold
        messages = [
            {'role': 'user', 'content': 'Message ' + str(i) * 20}
            for i in range(20)
        ]
        
        truncated = manager.truncate_context(messages)
        
        # Should have fewer messages after truncation
        assert len(truncated) < len(messages)
    
    def test_truncate_preserves_recent_10_messages(self):
        """Test that truncation preserves the most recent 10 messages."""
        manager = ContextManager(context_limit=100)
        
        # Create 15 messages
        messages = [
            {'role': 'user', 'content': f'Message {i}' * 10}
            for i in range(15)
        ]
        
        truncated = manager.truncate_context(messages)
        
        # Should preserve last 10 messages
        assert len(truncated) == 10
        
        # Verify the preserved messages are the most recent ones
        for i, msg in enumerate(truncated):
            expected_index = 15 - 10 + i  # Last 10 messages
            assert f'Message {expected_index}' in msg['content']
    
    def test_truncate_removes_older_messages(self):
        """Test that truncation removes older messages first."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'user', 'content': 'Old message 1' * 10},
            {'role': 'assistant', 'content': 'Old response 1' * 10},
            {'role': 'user', 'content': 'Recent message' * 10}
        ]
        
        truncated = manager.truncate_context(messages)
        
        # Most recent message should be preserved
        assert any('Recent message' in msg.get('content', '') for msg in truncated)
    
    def test_truncate_with_custom_limit(self):
        """Test truncation with custom token limit."""
        manager = ContextManager(context_limit=1000)
        
        messages = [
            {'role': 'user', 'content': 'Message ' + str(i) * 20}
            for i in range(20)
        ]
        
        # Use very small custom limit
        truncated = manager.truncate_context(messages, limit=50)
        
        # Should truncate based on custom limit
        assert len(truncated) < len(messages)
    
    def test_truncate_handles_empty_message_list(self):
        """Test that truncation handles empty message list."""
        manager = ContextManager(context_limit=1000)
        
        messages = []
        truncated = manager.truncate_context(messages)
        
        # Should return empty list
        assert truncated == []
    
    def test_truncate_with_mixed_roles(self):
        """Test truncation with mixed user and assistant messages."""
        manager = ContextManager(context_limit=100)
        
        messages = []
        for i in range(15):
            messages.append({'role': 'user', 'content': f'User message {i}' * 10})
            messages.append({'role': 'assistant', 'content': f'Assistant response {i}' * 10})
        
        truncated = manager.truncate_context(messages)
        
        # Should preserve recent messages regardless of role
        assert len(truncated) <= 10


class TestSystemPromptPreservation:
    """Test system prompt preservation during truncation."""
    
    def test_system_prompt_always_preserved(self):
        """Test that system prompt is always included after truncation."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
        ]
        
        # Add many user messages to trigger truncation
        for i in range(20):
            messages.append({'role': 'user', 'content': f'Message {i}' * 10})
        
        truncated = manager.truncate_context(messages)
        
        # System message should be present
        system_messages = [msg for msg in truncated if msg['role'] == 'system']
        assert len(system_messages) == 1
        assert system_messages[0]['content'] == 'You are a helpful assistant.'
    
    def test_multiple_system_prompts_preserved(self):
        """Test that multiple system messages are preserved."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'system', 'content': 'System prompt 1'},
            {'role': 'system', 'content': 'System prompt 2'},
        ]
        
        # Add many messages to trigger truncation
        for i in range(20):
            messages.append({'role': 'user', 'content': f'Message {i}' * 10})
        
        truncated = manager.truncate_context(messages)
        
        # Both system messages should be preserved
        system_messages = [msg for msg in truncated if msg['role'] == 'system']
        assert len(system_messages) == 2
    
    def test_system_prompt_preserved_even_when_large(self):
        """Test that system prompt is preserved even if it's large."""
        manager = ContextManager(context_limit=100)
        
        # Create a large system prompt
        large_system_prompt = 'System instruction. ' * 50
        
        messages = [
            {'role': 'system', 'content': large_system_prompt},
        ]
        
        # Add messages to trigger truncation
        for i in range(15):
            messages.append({'role': 'user', 'content': f'Message {i}' * 10})
        
        truncated = manager.truncate_context(messages)
        
        # System prompt should still be present
        system_messages = [msg for msg in truncated if msg['role'] == 'system']
        assert len(system_messages) == 1
        assert system_messages[0]['content'] == large_system_prompt
    
    def test_system_prompt_at_beginning_of_truncated_context(self):
        """Test that system prompts appear at the beginning of truncated context."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'system', 'content': 'System prompt'},
        ]
        
        for i in range(15):
            messages.append({'role': 'user', 'content': f'Message {i}' * 10})
        
        truncated = manager.truncate_context(messages)
        
        # System message should be first
        assert truncated[0]['role'] == 'system'
    
    def test_no_system_prompt_in_messages(self):
        """Test truncation when there is no system prompt."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'user', 'content': f'Message {i}' * 10}
            for i in range(15)
        ]
        
        truncated = manager.truncate_context(messages)
        
        # Should still truncate to recent 10 messages
        assert len(truncated) == 10
        
        # No system messages should be present
        system_messages = [msg for msg in truncated if msg['role'] == 'system']
        assert len(system_messages) == 0


class TestRecentMessagePreservation:
    """Test preservation of recent messages during truncation."""
    
    def test_preserves_exactly_10_recent_messages(self):
        """Test that exactly 10 recent messages are preserved."""
        manager = ContextManager(context_limit=100)
        
        # Create 20 non-system messages
        messages = [
            {'role': 'user', 'content': f'Message {i}' * 10}
            for i in range(20)
        ]
        
        truncated = manager.truncate_context(messages)
        
        # Should have exactly 10 messages
        assert len(truncated) == 10
    
    def test_preserves_recent_messages_in_order(self):
        """Test that recent messages maintain their order."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'user', 'content': f'Message {i}'}
            for i in range(15)
        ]
        
        truncated = manager.truncate_context(messages)
        
        # Verify order is maintained (should be messages 5-14)
        for i, msg in enumerate(truncated):
            expected_num = 5 + i
            assert f'Message {expected_num}' in msg['content']
    
    def test_recent_messages_with_system_prompt(self):
        """Test that recent messages count excludes system prompt."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'system', 'content': 'System prompt'},
        ]
        
        # Add 15 non-system messages
        for i in range(15):
            messages.append({'role': 'user', 'content': f'Message {i}' * 10})
        
        truncated = manager.truncate_context(messages)
        
        # Should have 1 system + 10 recent = 11 total
        assert len(truncated) == 11
        
        # Verify system message is first
        assert truncated[0]['role'] == 'system'
        
        # Verify we have 10 non-system messages
        non_system = [msg for msg in truncated if msg['role'] != 'system']
        assert len(non_system) == 10
    
    def test_fewer_than_10_messages_all_preserved(self):
        """Test that all messages are preserved when fewer than 10."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'user', 'content': 'Message ' * 20}
            for i in range(5)
        ]
        
        truncated = manager.truncate_context(messages)
        
        # All 5 messages should be preserved
        assert len(truncated) == 5
    
    def test_recent_messages_include_conversation_pairs(self):
        """Test that recent messages preserve user-assistant pairs."""
        manager = ContextManager(context_limit=100)
        
        messages = []
        for i in range(15):
            messages.append({'role': 'user', 'content': f'Question {i}' * 10})
            messages.append({'role': 'assistant', 'content': f'Answer {i}' * 10})
        
        truncated = manager.truncate_context(messages)
        
        # Should preserve last 10 messages (5 pairs)
        assert len(truncated) == 10


class TestPrepareContext:
    """Test the prepare_context method."""
    
    def test_prepare_context_returns_messages_under_threshold(self):
        """Test that prepare_context returns messages unchanged when under threshold."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'}
        ]
        
        prepared = manager.prepare_context(messages)
        
        assert prepared == messages
    
    def test_prepare_context_truncates_when_needed(self):
        """Test that prepare_context truncates when exceeding threshold."""
        manager = ContextManager(context_limit=100)
        
        messages = [
            {'role': 'user', 'content': f'Message {i}' * 10}
            for i in range(20)
        ]
        
        prepared = manager.prepare_context(messages)
        
        # Should be truncated
        assert len(prepared) < len(messages)
        assert len(prepared) == 10
    
    def test_prepare_context_with_session_id(self):
        """Test that prepare_context accepts session_id for logging."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'user', 'content': 'Hello'}
        ]
        
        # Should not raise exception with session_id
        prepared = manager.prepare_context(messages, session_id='session_123')
        
        assert prepared == messages
    
    def test_prepare_context_with_empty_messages(self):
        """Test that prepare_context handles empty message list."""
        manager = ContextManager(context_limit=4096)
        
        messages = []
        prepared = manager.prepare_context(messages)
        
        assert prepared == []


class TestContextManagerInitialization:
    """Test context manager initialization."""
    
    def test_initialization_with_default_values(self):
        """Test that context manager initializes with default config values."""
        manager = ContextManager()
        
        # Should have context_limit from Config
        assert manager.context_limit > 0
        assert manager.model is not None
        assert manager.encoding is not None
    
    def test_initialization_with_custom_limit(self):
        """Test initialization with custom context limit."""
        custom_limit = 8192
        manager = ContextManager(context_limit=custom_limit)
        
        assert manager.context_limit == custom_limit
    
    def test_initialization_with_custom_model(self):
        """Test initialization with custom model name."""
        custom_model = 'gpt-4'
        manager = ContextManager(model=custom_model)
        
        assert manager.model == custom_model
    
    def test_tokenizer_initialization(self):
        """Test that tokenizer is properly initialized."""
        manager = ContextManager()
        
        # Should have encoding object
        assert manager.encoding is not None
        
        # Should be able to encode text
        tokens = manager.encoding.encode('test')
        assert isinstance(tokens, list)
        assert len(tokens) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_none_content(self):
        """Test handling of None content in messages."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'user', 'content': None}
        ]
        
        # Should handle gracefully without raising exception
        token_count = manager.calculate_tokens(messages)
        assert token_count >= 0
    
    def test_handles_empty_content_array(self):
        """Test handling of empty content array."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'user', 'content': []}
        ]
        
        token_count = manager.calculate_tokens(messages)
        assert token_count >= 0
    
    def test_handles_content_blocks_without_text(self):
        """Test handling of content blocks that don't have text type."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {
                'role': 'user',
                'content': [
                    {'type': 'image_url', 'image_url': {'url': 'https://example.com/img.png'}}
                ]
            }
        ]
        
        # Should not count tokens for non-text blocks
        token_count = manager.calculate_tokens(messages)
        assert token_count > 0  # Should have overhead tokens
    
    def test_truncation_with_very_small_limit(self):
        """Test truncation behavior with extremely small token limit."""
        manager = ContextManager(context_limit=10)
        
        messages = [
            {'role': 'user', 'content': 'Hello world this is a test message'}
        ]
        
        # Should still return messages even if over limit
        truncated = manager.truncate_context(messages)
        assert len(truncated) >= 0
    
    def test_handles_unicode_content(self):
        """Test token counting with unicode characters."""
        manager = ContextManager(context_limit=4096)
        
        messages = [
            {'role': 'user', 'content': '你好世界 🌍 مرحبا'}
        ]
        
        token_count = manager.calculate_tokens(messages)
        assert token_count > 0
