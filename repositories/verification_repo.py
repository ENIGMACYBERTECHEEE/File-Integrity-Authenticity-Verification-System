"""
Verification repository for database operations.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from database import get_collection
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class VerificationRepository:
    """Repository for verification records operations."""
    
    def __init__(self):
        """Initialize verification repository."""
        self.collection = get_collection("verifications")
    
    def create_verification(self, verification_data: Dict[str, Any]) -> str:
        """
        Create a new verification record.
        
        Args:
            verification_data: Verification data dictionary
            
        Returns:
            str: Verification record ID
        """
        try:
            verification_data["timestamp"] = datetime.utcnow()
            
            result = self.collection.insert_one(verification_data)
            logger.info(f"Verification record created for file: {verification_data['file_id']}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating verification record: {str(e)}")
            raise ValueError(f"Failed to create verification record: {str(e)}")
    
    def get_verification_by_id(self, verification_id: str) -> Optional[Dict[str, Any]]:
        """
        Get verification by ID.
        
        Args:
            verification_id: Verification record ID
            
        Returns:
            Optional[Dict[str, Any]]: Verification data or None
        """
        try:
            verification = self.collection.find_one({"_id": ObjectId(verification_id)})
            if verification:
                verification["_id"] = str(verification["_id"])
            return verification
        except Exception as e:
            logger.error(f"Error getting verification by ID: {str(e)}")
            return None
    
    def get_verifications_by_file(self, file_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get verification history for a file.
        
        Args:
            file_id: File ID
            limit: Maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: List of verification records
        """
        try:
            verifications = list(
                self.collection.find({"file_id": file_id})
                .sort("timestamp", -1)
                .limit(limit)
            )
            for verification in verifications:
                verification["_id"] = str(verification["_id"])
            return verifications
        except Exception as e:
            logger.error(f"Error getting verifications by file: {str(e)}")
            return []
    
    def get_verifications_by_user(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get verification history for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: List of verification records
        """
        try:
            verifications = list(
                self.collection.find({"user_id": user_id})
                .sort("timestamp", -1)
                .limit(limit)
            )
            for verification in verifications:
                verification["_id"] = str(verification["_id"])
            return verifications
        except Exception as e:
            logger.error(f"Error getting verifications by user: {str(e)}")
            return []
    
    def get_latest_verification(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest verification for a file.
        
        Args:
            file_id: File ID
            
        Returns:
            Optional[Dict[str, Any]]: Latest verification record or None
        """
        try:
            verification = self.collection.find_one(
                {"file_id": file_id},
                sort=[("timestamp", -1)]
            )
            if verification:
                verification["_id"] = str(verification["_id"])
            return verification
        except Exception as e:
            logger.error(f"Error getting latest verification: {str(e)}")
            return None
    
    def get_failed_verifications(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get failed verification records.
        
        Args:
            user_id: Optional user ID to filter by
            limit: Maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: List of failed verification records
        """
        try:
            query = {"verified": False}
            if user_id:
                query["user_id"] = user_id
            
            verifications = list(
                self.collection.find(query)
                .sort("timestamp", -1)
                .limit(limit)
            )
            for verification in verifications:
                verification["_id"] = str(verification["_id"])
            return verifications
        except Exception as e:
            logger.error(f"Error getting failed verifications: {str(e)}")
            return []


verification_repository = VerificationRepository()
