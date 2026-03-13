"""Application configuration."""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://user:password@localhost:3306/multimodal_assistant'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173').split(',')
    
    # LLM Provider
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_ENDPOINT = os.getenv('LLM_ENDPOINT', 'https://api.deepseek.com/v1/chat/completions')
    LLM_MODEL = os.getenv('LLM_MODEL', 'deepseek-chat')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0.7'))
    LLM_MAX_TOKENS = int(os.getenv('LLM_MAX_TOKENS', '4096'))
    LLM_TOP_P = float(os.getenv('LLM_TOP_P', '1.0'))
    LLM_CONTEXT_LIMIT = int(os.getenv('LLM_CONTEXT_LIMIT', '32000'))
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {
        'image/png', 'image/jpeg', 'image/gif',
        'application/pdf', 'audio/mpeg', 'audio/wav'
    }
    
    @classmethod
    def validate(cls):
        """Validate required configuration values at startup.
        
        Validates that all required configuration values are present and not using
        default development values. Raises ValueError if validation fails.
        
        Skips validation in test environments (TESTING=True).
        
        Requirements: 19.1, 19.2, 19.3
        """
        # Skip validation in test environments
        if getattr(cls, 'TESTING', False):
            return
        
        errors = []
        
        # Validate SECRET_KEY
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key or secret_key.startswith('dev-'):
            errors.append("SECRET_KEY must be set and not use default development value")
        
        # Validate JWT_SECRET_KEY
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        if not jwt_secret or jwt_secret.startswith('jwt-'):
            errors.append("JWT_SECRET_KEY must be set and not use default development value")
        
        # Validate LLM_API_KEY
        llm_api_key = os.getenv('LLM_API_KEY')
        if not llm_api_key:
            errors.append("LLM_API_KEY must be set")
        
        # Validate DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            errors.append("DATABASE_URL must be set")
        
        # Validate LLM_ENDPOINT
        llm_endpoint = os.getenv('LLM_ENDPOINT')
        if not llm_endpoint:
            errors.append("LLM_ENDPOINT must be set")
        
        # Validate model parameters are within valid ranges (Requirement 19.4)
        try:
            temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
            if not 0.0 <= temperature <= 2.0:
                errors.append("LLM_TEMPERATURE must be between 0.0 and 2.0")
        except ValueError:
            errors.append("LLM_TEMPERATURE must be a valid float")
        
        try:
            max_tokens = int(os.getenv('LLM_MAX_TOKENS', '4096'))
            if max_tokens <= 0:
                errors.append("LLM_MAX_TOKENS must be a positive integer")
        except ValueError:
            errors.append("LLM_MAX_TOKENS must be a valid integer")
        
        try:
            top_p = float(os.getenv('LLM_TOP_P', '1.0'))
            if not 0.0 <= top_p <= 1.0:
                errors.append("LLM_TOP_P must be between 0.0 and 1.0")
        except ValueError:
            errors.append("LLM_TOP_P must be a valid float")
        
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_message)
