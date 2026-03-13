"""Authentication service for password hashing and JWT token management."""
import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta


class AuthService:
    """Service for handling authentication operations."""
    
    # Bcrypt cost factor as specified in requirements
    BCRYPT_COST_FACTOR = 12
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt with cost factor 12.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password as a string
        """
        # Generate salt and hash password
        salt = bcrypt.gensalt(rounds=AuthService.BCRYPT_COST_FACTOR)
        password_bytes = password.encode('utf-8')
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    @staticmethod
    def generate_token(user_id: str, username: str) -> str:
        """
        Generate a JWT token with 24-hour expiration.
        
        Args:
            user_id: User's unique identifier
            username: User's username
            
        Returns:
            JWT token string
        """
        # Create token with user identity and additional claims
        additional_claims = {
            'username': username
        }
        
        # Token expires in 24 hours as per requirements
        token = create_access_token(
            identity=user_id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )
        
        return token
