"""
Key repository for cryptographic keys storage.
"""
from typing import Optional, Dict, Any
from database import get_collection
import logging

logger = logging.getLogger(__name__)


class KeyRepository:
    """Repository for cryptographic keys operations."""
    
    def __init__(self):
        """Initialize key repository."""
        self.collection = get_collection("keys")
    
    def store_keys(self, user_id: str, public_key: bytes, encrypted_private_key: bytes) -> bool:
        """
        Store user's RSA key pair.
        
        Args:
            user_id: User ID
            public_key: Public key in PEM format
            encrypted_private_key: Encrypted private key in PEM format
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            key_data = {
                "user_id": user_id,
                "public_key": public_key.decode('utf-8'),
                "encrypted_private_key": encrypted_private_key.decode('utf-8')
            }
            
            # Upsert: update if exists, insert if not
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": key_data},
                upsert=True
            )
            logger.info(f"Keys stored for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error storing keys: {str(e)}")
            return False
    
    def get_keys(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user's RSA key pair.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[Dict[str, Any]]: Key data or None
        """
        try:
            keys = self.collection.find_one({"user_id": user_id})
            if keys:
                keys["_id"] = str(keys["_id"])
            return keys
        except Exception as e:
            logger.error(f"Error getting keys: {str(e)}")
            return None
    
    def get_public_key(self, user_id: str) -> Optional[str]:
        """
        Get user's public key.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[str]: Public key in PEM format or None
        """
        try:
            keys = self.collection.find_one({"user_id": user_id})
            return keys["public_key"] if keys else None
        except Exception as e:
            logger.error(f"Error getting public key: {str(e)}")
            return None
    
    def get_encrypted_private_key(self, user_id: str) -> Optional[str]:
        """
        Get user's encrypted private key.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[str]: Encrypted private key in PEM format or None
        """
        try:
            keys = self.collection.find_one({"user_id": user_id})
            return keys["encrypted_private_key"] if keys else None
        except Exception as e:
            logger.error(f"Error getting encrypted private key: {str(e)}")
            return None
    
    def delete_keys(self, user_id: str) -> bool:
        """
        Delete user's keys.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.collection.delete_one({"user_id": user_id})
            logger.info(f"Keys deleted for user: {user_id}")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting keys: {str(e)}")
            return False


key_repository = KeyRepository()
