"""
Authentication service for user registration and login.
"""
from typing import Optional, Dict, Any
import bcrypt
from repositories.user_repo import user_repository
from repositories.key_repo import key_repository
from security.jwt_utils import jwt_handler
from security.rsa import rsa_handler
from config import config
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for user management."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        Automatically truncates password to 72 bytes to comply with bcrypt limitation.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        Automatically truncates password to 72 bytes to comply with bcrypt limitation.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            bool: True if password matches, False otherwise
        """
        # Bcrypt has a 72-byte limit, truncate if necessary
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    @staticmethod
    def register_user(username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            
        Returns:
            Dict[str, Any]: Registration result with user_id and message
            
        Raises:
            ValueError: If registration fails
        """
        # Validate password length
        if len(password) < config.PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {config.PASSWORD_MIN_LENGTH} characters long")
        
        # Check if user already exists
        if user_repository.user_exists(username=username):
            raise ValueError("Username already exists")
        
        if user_repository.user_exists(email=email):
            raise ValueError("Email already exists")
        
        # Generate RSA key pair
        try:
            private_key_pem, public_key_pem = rsa_handler.generate_key_pair()
            encrypted_private_key = rsa_handler.encrypt_private_key(private_key_pem, password)
        except Exception as e:
            logger.error(f"Error generating RSA keys: {str(e)}")
            raise ValueError("Failed to generate encryption keys")
        
        # Hash password
        password_hash = AuthService.hash_password(password)
        
        # Create user
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "rsa_public_key": public_key_pem.decode('utf-8'),
            "rsa_private_key_encrypted": encrypted_private_key.decode('utf-8')
        }
        
        try:
            user_id = user_repository.create_user(user_data)
            
            # Store keys in key repository
            key_repository.store_keys(user_id, public_key_pem, encrypted_private_key)
            
            logger.info(f"User registered successfully: {username}")
            return {
                "user_id": user_id,
                "username": username,
                "message": "User registered successfully"
            }
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise ValueError(f"Registration failed: {str(e)}")
    
    @staticmethod
    def login_user(username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user and generate access token.
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            Dict[str, Any]: Login result with access_token and user info
            
        Raises:
            ValueError: If authentication fails
        """
        # Get user by username
        user = user_repository.get_user_by_username(username)
        
        if not user:
            raise ValueError("Invalid username or password")
        
        if not user.get("is_active", False):
            raise ValueError("Account is inactive")
        
        # Verify password
        if not AuthService.verify_password(password, user["password_hash"]):
            raise ValueError("Invalid username or password")
        
        # Generate JWT token
        token_data = {
            "sub": user["_id"],
            "username": user["username"],
            "email": user["email"]
        }
        
        access_token = jwt_handler.create_access_token(token_data)
        
        logger.info(f"User logged in successfully: {username}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["_id"],
            "username": user["username"],
            "email": user["email"]
        }
    
    @staticmethod
    def get_current_user(token: str) -> Optional[Dict[str, Any]]:
        """
        Get current user from JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            Optional[Dict[str, Any]]: User data or None
        """
        payload = jwt_handler.decode_token(token)
        
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = user_repository.get_user_by_id(user_id)
        return user
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """
        Validate JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        return jwt_handler.verify_token(token)


auth_service = AuthService()
