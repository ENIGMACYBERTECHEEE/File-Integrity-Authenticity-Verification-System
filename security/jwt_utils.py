"""
JWT token creation and validation utilities.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from config import config


class JWTHandler:
    """JWT token creation and validation handler."""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.JWT_EXPIRATION_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(
            to_encode,
            config.JWT_SECRET_KEY,
            algorithm=config.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: JWT token to decode
            
        Returns:
            Optional[Dict[str, Any]]: Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET_KEY,
                algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def verify_token(token: str) -> bool:
        """
        Verify if a JWT token is valid.
        
        Args:
            token: JWT token to verify
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        payload = JWTHandler.decode_token(token)
        return payload is not None


jwt_handler = JWTHandler()
