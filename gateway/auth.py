"""
JWT authentication utilities for FastAPI.
"""
from typing import Optional
from fastapi import HTTPException, status
from services.auth_service import auth_service


def verify_token(token: str) -> bool:
    """
    Verify JWT token validity.
    
    Args:
        token: JWT token
        
    Returns:
        bool: True if valid, False otherwise
    """
    return auth_service.validate_token(token)


def get_user_from_token(token: str) -> Optional[dict]:
    """
    Extract user data from JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        Optional[dict]: User data or None
    """
    user = auth_service.get_current_user(token)
    return user


def create_token_response(username: str, password: str) -> dict:
    """
    Create token response for login.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        dict: Token response
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        result = auth_service.login_user(username, password)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
