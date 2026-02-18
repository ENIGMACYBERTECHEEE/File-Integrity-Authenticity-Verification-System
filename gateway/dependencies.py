"""
Shared dependencies for FastAPI application.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.auth_service import auth_service
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        dict: Current user data
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    user = auth_service.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    return user


async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Dependency to get current user if token is provided, None otherwise.
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        
    Returns:
        Optional[dict]: Current user data or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def get_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to get current user and verify admin privileges.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        dict: Current admin user data
        
    Raises:
        HTTPException: If user is not an admin
    """
    # Check both is_admin and role fields for compatibility
    is_admin = current_user.get("is_admin", False) or current_user.get("role") == "admin"
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation"
        )
    
    return current_user
