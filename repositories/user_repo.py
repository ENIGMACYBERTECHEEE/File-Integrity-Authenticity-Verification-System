"""
User repository for database operations.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from database import get_collection
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user data operations."""
    
    def __init__(self):
        """Initialize user repository."""
        self.collection = get_collection("users")
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user.
        
        Args:
            user_data: User data dictionary
            
        Returns:
            str: User ID
            
        Raises:
            ValueError: If user already exists
        """
        try:
            user_data["created_at"] = datetime.utcnow()
            user_data["is_active"] = True
            user_data["role"] = user_data.get("role", "user")
            
            result = self.collection.insert_one(user_data)
            logger.info(f"User created: {user_data['username']}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise ValueError(f"Failed to create user: {str(e)}")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[Dict[str, Any]]: User data or None
        """
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            Optional[Dict[str, Any]]: User data or None
        """
        try:
            user = self.collection.find_one({"username": username})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            Optional[Dict[str, Any]]: User data or None
        """
        try:
            user = self.collection.find_one({"email": email})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update user data.
        
        Args:
            user_id: User ID
            update_data: Data to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete user (soft delete by setting is_active to False).
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": False}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False
    
    def user_exists(self, username: str = None, email: str = None) -> bool:
        """
        Check if user exists by username or email.
        
        Args:
            username: Username to check
            email: Email to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        query = {}
        if username:
            query["username"] = username
        if email:
            query["email"] = email
        
        if not query:
            return False
        
        return self.collection.find_one(query) is not None


user_repository = UserRepository()
