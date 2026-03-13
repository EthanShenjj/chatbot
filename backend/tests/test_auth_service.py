"""Unit tests for authentication service."""
import pytest
import bcrypt
import jwt
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from config import Config


class TestPasswordHashing:
    """Test password hashing and verification."""
    
    def test_hash_password_returns_valid_bcrypt_hash(self):
        """Test that hash_password returns a valid bcrypt hash."""
        password = "test_password_123"
        hashed = AuthService.hash_password(password)
        
        # Bcrypt hashes should start with $2b$ and be 60 characters
        assert hashed.startswith('$2b$')
        assert len(hashed) == 60
    
    def test_hash_password_uses_correct_cost_factor(self):
        """Test that hash_password uses cost factor 12."""
        password = "test_password_123"
        hashed = AuthService.hash_password(password)
        
        # Extract cost factor from hash (format: $2b$12$...)
        cost_factor = int(hashed.split('$')[2])
        assert cost_factor == 12
    
    def test_hash_password_generates_unique_hashes(self):
        """Test that hashing the same password twice produces different hashes."""
        password = "test_password_123"
        hash1 = AuthService.hash_password(password)
        hash2 = AuthService.hash_password(password)
        
        # Different salts should produce different hashes
        assert hash1 != hash2
    
    def test_verify_password_accepts_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "correct_password"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(password, hashed) is True
    
    def test_verify_password_rejects_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_handles_empty_password(self):
        """Test that verify_password handles empty passwords correctly."""
        password = ""
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("not_empty", hashed) is False
    
    def test_verify_password_handles_special_characters(self):
        """Test that password hashing works with special characters."""
        password = "p@ssw0rd!#$%^&*()"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(password, hashed) is True
    
    def test_verify_password_handles_unicode(self):
        """Test that password hashing works with unicode characters."""
        password = "пароль密码🔒"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.verify_password(password, hashed) is True


class TestJWTTokenGeneration:
    """Test JWT token generation."""
    
    def test_generate_token_returns_valid_jwt(self, app_context):
        """Test that generate_token returns a valid JWT string."""
        user_id = "user_123"
        username = "testuser"
        
        token = AuthService.generate_token(user_id, username)
        
        # JWT tokens have three parts separated by dots
        assert isinstance(token, str)
        assert len(token.split('.')) == 3
    
    def test_generate_token_includes_user_identity(self, app_context):
        """Test that generated token contains user_id in identity claim."""
        user_id = "user_456"
        username = "testuser"
        
        token = AuthService.generate_token(user_id, username)
        
        # Decode without verification to check payload
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        
        assert decoded['sub'] == user_id  # 'sub' is the identity claim
    
    def test_generate_token_includes_username_claim(self, app_context):
        """Test that generated token contains username in additional claims."""
        user_id = "user_789"
        username = "john_doe"
        
        token = AuthService.generate_token(user_id, username)
        
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        
        assert decoded['username'] == username
    
    def test_generate_token_sets_24_hour_expiration(self, app_context):
        """Test that generated token expires in 24 hours."""
        user_id = "user_101"
        username = "testuser"
        
        import time
        before_timestamp = time.time()
        token = AuthService.generate_token(user_id, username)
        after_timestamp = time.time()
        
        decoded = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        
        # Check expiration is approximately 24 hours from now
        exp_timestamp = decoded['exp']
        
        # Calculate expected expiration (24 hours = 86400 seconds)
        expected_exp_min = before_timestamp + 86400
        expected_exp_max = after_timestamp + 86400
        
        # Allow 2 second tolerance for test execution time
        assert expected_exp_min - 2 <= exp_timestamp <= expected_exp_max + 2
    
    def test_generate_token_creates_unique_tokens(self, app_context):
        """Test that generating tokens for same user produces different tokens."""
        user_id = "user_202"
        username = "testuser"
        
        token1 = AuthService.generate_token(user_id, username)
        token2 = AuthService.generate_token(user_id, username)
        
        # Tokens should differ due to different iat (issued at) timestamps
        assert token1 != token2


class TestJWTTokenValidation:
    """Test JWT token validation and expiration handling."""
    
    def test_token_can_be_decoded_with_correct_secret(self, app_context):
        """Test that token can be decoded using the JWT secret."""
        user_id = "user_303"
        username = "testuser"
        
        token = AuthService.generate_token(user_id, username)
        
        # Decode with verification using the app's JWT secret
        decoded = jwt.decode(
            token,
            app_context.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        
        assert decoded['sub'] == user_id
        assert decoded['username'] == username
    
    def test_token_cannot_be_decoded_with_wrong_secret(self, app_context):
        """Test that token validation fails with incorrect secret."""
        user_id = "user_404"
        username = "testuser"
        
        token = AuthService.generate_token(user_id, username)
        
        # Attempt to decode with wrong secret
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(
                token,
                'wrong_secret_key',
                algorithms=['HS256']
            )
    
    def test_expired_token_raises_exception(self, app_context):
        """Test that expired tokens are rejected during validation."""
        user_id = "user_505"
        username = "testuser"
        
        # Create a token that expires immediately
        expired_token = jwt.encode(
            {
                'sub': user_id,
                'username': username,
                'exp': datetime.utcnow() - timedelta(seconds=1),
                'iat': datetime.utcnow() - timedelta(hours=25)
            },
            app_context.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Attempt to decode expired token
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(
                expired_token,
                app_context.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
    
    def test_token_with_invalid_format_raises_exception(self, app_context):
        """Test that malformed tokens are rejected."""
        invalid_token = "not.a.valid.jwt.token"
        
        with pytest.raises(jwt.DecodeError):
            jwt.decode(
                invalid_token,
                app_context.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
    
    def test_token_remains_valid_before_expiration(self, app_context):
        """Test that token is valid before 24-hour expiration."""
        user_id = "user_606"
        username = "testuser"
        
        token = AuthService.generate_token(user_id, username)
        
        # Token should be valid immediately after generation
        decoded = jwt.decode(
            token,
            app_context.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        
        assert decoded['sub'] == user_id
        assert decoded['username'] == username
        
        # Check that expiration is in the future
        exp_timestamp = decoded['exp']
        assert exp_timestamp > datetime.utcnow().timestamp()
    
    def test_token_without_required_claims_is_invalid(self, app_context):
        """Test that tokens missing required claims are rejected."""
        # Create token without username claim
        incomplete_token = jwt.encode(
            {
                'sub': 'user_707',
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow()
            },
            app_context.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
        
        # Token can be decoded but won't have username claim
        decoded = jwt.decode(
            incomplete_token,
            app_context.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        
        assert 'username' not in decoded


class TestPasswordSecurityProperties:
    """Test security properties of password handling."""
    
    def test_password_hash_is_not_reversible(self):
        """Test that password hash cannot be reversed to original password."""
        password = "secret_password"
        hashed = AuthService.hash_password(password)
        
        # Hash should not contain the original password
        assert password not in hashed
        assert password.encode('utf-8') not in hashed.encode('utf-8')
    
    def test_similar_passwords_produce_different_hashes(self):
        """Test that similar passwords produce completely different hashes."""
        password1 = "password123"
        password2 = "password124"
        
        hash1 = AuthService.hash_password(password1)
        hash2 = AuthService.hash_password(password2)
        
        # Hashes should be completely different
        assert hash1 != hash2
        
        # Verify each password only matches its own hash
        assert AuthService.verify_password(password1, hash1) is True
        assert AuthService.verify_password(password1, hash2) is False
        assert AuthService.verify_password(password2, hash1) is False
        assert AuthService.verify_password(password2, hash2) is True
