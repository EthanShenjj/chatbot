"""Tests for configuration management.

**Validates: Requirements 19.1, 19.2, 19.3, 19.4**
"""
import os
import pytest
from unittest.mock import patch
from config import Config


class TestConfigValidation:
    """Test configuration validation at startup."""
    
    def test_validate_with_all_required_config(self):
        """Test validation passes when all required config is present.
        
        **Validates: Requirements 19.1, 19.2**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            # Should not raise
            Config.validate()
    
    def test_validate_fails_without_secret_key(self):
        """Test validation fails when SECRET_KEY is missing.
        
        **Validates: Requirements 19.2, 19.3**
        """
        with patch.dict(os.environ, {
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'SECRET_KEY' in str(exc_info.value)
    
    def test_validate_fails_with_dev_secret_key(self):
        """Test validation fails when SECRET_KEY uses development default.
        
        **Validates: Requirements 19.2, 19.3**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'dev-secret-key-change-in-production',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'SECRET_KEY' in str(exc_info.value)
            assert 'default development value' in str(exc_info.value)
    
    def test_validate_fails_without_jwt_secret(self):
        """Test validation fails when JWT_SECRET_KEY is missing.
        
        **Validates: Requirements 19.2, 19.3**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'JWT_SECRET_KEY' in str(exc_info.value)
    
    def test_validate_fails_with_dev_jwt_secret(self):
        """Test validation fails when JWT_SECRET_KEY uses development default.
        
        **Validates: Requirements 19.2, 19.3**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'jwt-secret-key-change-in-production',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'JWT_SECRET_KEY' in str(exc_info.value)
            assert 'default development value' in str(exc_info.value)
    
    def test_validate_fails_without_llm_api_key(self):
        """Test validation fails when LLM_API_KEY is missing.
        
        **Validates: Requirements 19.1, 19.2, 19.3**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_API_KEY' in str(exc_info.value)
    
    def test_validate_fails_without_database_url(self):
        """Test validation fails when DATABASE_URL is missing.
        
        **Validates: Requirements 19.1, 19.2, 19.3**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'DATABASE_URL' in str(exc_info.value)
    
    def test_validate_fails_without_llm_endpoint(self):
        """Test validation fails when LLM_ENDPOINT is missing.
        
        **Validates: Requirements 19.1, 19.2, 19.3**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_ENDPOINT' in str(exc_info.value)
    
    def test_validate_fails_with_multiple_missing_configs(self):
        """Test validation reports all missing configuration values.
        
        **Validates: Requirements 19.2, 19.3**
        """
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            error_msg = str(exc_info.value)
            assert 'SECRET_KEY' in error_msg
            assert 'JWT_SECRET_KEY' in error_msg
            assert 'LLM_API_KEY' in error_msg
            assert 'DATABASE_URL' in error_msg
            assert 'LLM_ENDPOINT' in error_msg


class TestModelParameterConfiguration:
    """Test model parameter configuration and validation.
    
    **Validates: Requirement 19.4**
    """
    
    def test_temperature_within_valid_range(self):
        """Test temperature parameter accepts valid values (0.0 to 2.0).
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TEMPERATURE': '1.5'
        }, clear=True):
            # Should not raise - validation passes for valid temperature
            Config.validate()
    
    def test_temperature_below_minimum_fails(self):
        """Test temperature below 0.0 fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TEMPERATURE': '-0.1'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_TEMPERATURE' in str(exc_info.value)
            assert 'between 0.0 and 2.0' in str(exc_info.value)
    
    def test_temperature_above_maximum_fails(self):
        """Test temperature above 2.0 fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TEMPERATURE': '2.5'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_TEMPERATURE' in str(exc_info.value)
            assert 'between 0.0 and 2.0' in str(exc_info.value)
    
    def test_temperature_invalid_format_fails(self):
        """Test non-numeric temperature fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TEMPERATURE': 'invalid'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_TEMPERATURE' in str(exc_info.value)
            assert 'valid float' in str(exc_info.value)
    
    def test_max_tokens_positive_integer(self):
        """Test max_tokens parameter accepts positive integers.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_MAX_TOKENS': '8192'
        }, clear=True):
            # Should not raise - validation passes for valid max_tokens
            Config.validate()
    
    def test_max_tokens_zero_fails(self):
        """Test max_tokens of zero fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_MAX_TOKENS': '0'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_MAX_TOKENS' in str(exc_info.value)
            assert 'positive integer' in str(exc_info.value)
    
    def test_max_tokens_negative_fails(self):
        """Test negative max_tokens fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_MAX_TOKENS': '-100'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_MAX_TOKENS' in str(exc_info.value)
            assert 'positive integer' in str(exc_info.value)
    
    def test_max_tokens_invalid_format_fails(self):
        """Test non-integer max_tokens fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_MAX_TOKENS': 'invalid'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_MAX_TOKENS' in str(exc_info.value)
            assert 'valid integer' in str(exc_info.value)
    
    def test_top_p_within_valid_range(self):
        """Test top_p parameter accepts valid values (0.0 to 1.0).
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TOP_P': '0.9'
        }, clear=True):
            # Should not raise - validation passes for valid top_p
            Config.validate()
    
    def test_top_p_below_minimum_fails(self):
        """Test top_p below 0.0 fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TOP_P': '-0.1'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_TOP_P' in str(exc_info.value)
            assert 'between 0.0 and 1.0' in str(exc_info.value)
    
    def test_top_p_above_maximum_fails(self):
        """Test top_p above 1.0 fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TOP_P': '1.5'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_TOP_P' in str(exc_info.value)
            assert 'between 0.0 and 1.0' in str(exc_info.value)
    
    def test_top_p_invalid_format_fails(self):
        """Test non-numeric top_p fails validation.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions',
            'LLM_TOP_P': 'invalid'
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Config.validate()
            assert 'LLM_TOP_P' in str(exc_info.value)
            assert 'valid float' in str(exc_info.value)
    
    def test_default_model_parameters(self):
        """Test default model parameters are set correctly.
        
        **Validates: Requirement 19.4**
        """
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'mysql+pymysql://user:pass@localhost/db',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            # Should not raise - validation passes with default parameters
            Config.validate()


class TestAppStartupValidation:
    """Test that app initialization validates configuration.
    
    **Validates: Requirements 19.2, 19.3**
    """
    
    def test_app_refuses_to_start_with_invalid_config(self):
        """Test app refuses to start when required configuration is missing.
        
        **Validates: Requirement 19.3**
        """
        from app import create_app
        
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                create_app()
            assert 'Configuration validation failed' in str(exc_info.value)
    
    def test_app_starts_with_valid_config(self):
        """Test app starts successfully with valid configuration.
        
        **Validates: Requirement 19.2**
        """
        from app import create_app
        
        with patch.dict(os.environ, {
            'SECRET_KEY': 'production-secret-key',
            'JWT_SECRET_KEY': 'production-jwt-secret',
            'LLM_API_KEY': 'sk-test-api-key',
            'DATABASE_URL': 'sqlite:///:memory:',
            'LLM_ENDPOINT': 'https://api.example.com/v1/chat/completions'
        }, clear=True):
            app = create_app()
            assert app is not None
