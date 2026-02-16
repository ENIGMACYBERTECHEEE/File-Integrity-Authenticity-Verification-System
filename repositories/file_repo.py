"""
File repository for database operations.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from database import get_collection
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class FileRepository:
    """Repository for file metadata operations."""
    
    def __init__(self):
        """Initialize file repository."""
        self.collection = get_collection("files")
    
    def create_file(self, file_data: Dict[str, Any]) -> str:
        """
        Create a new file record.
        
        Args:
            file_data: File metadata dictionary
            
        Returns:
            str: File record ID
        """
        try:
            file_data["upload_date"] = datetime.utcnow()
            file_data["last_verified"] = None
            file_data["verification_count"] = 0
            file_data["is_deleted"] = False
            
            result = self.collection.insert_one(file_data)
            logger.info(f"File record created: {file_data['file_id']}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating file record: {str(e)}")
            raise ValueError(f"Failed to create file record: {str(e)}")
    
    def get_file_by_id(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file by record ID.
        
        Args:
            record_id: File record ID
            
        Returns:
            Optional[Dict[str, Any]]: File metadata or None
        """
        try:
            file = self.collection.find_one({"_id": ObjectId(record_id)})
            if file:
                file["_id"] = str(file["_id"])
            return file
        except Exception as e:
            logger.error(f"Error getting file by ID: {str(e)}")
            return None
    
    def get_file_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file by file_id.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Optional[Dict[str, Any]]: File metadata or None
        """
        try:
            file = self.collection.find_one({"file_id": file_id, "is_deleted": False})
            if file:
                file["_id"] = str(file["_id"])
            return file
        except Exception as e:
            logger.error(f"Error getting file by file_id: {str(e)}")
            return None
    
    def get_files_by_user(self, user_id: str, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        Get all files for a user.
        
        Args:
            user_id: User ID
            include_deleted: Whether to include deleted files
            
        Returns:
            List[Dict[str, Any]]: List of file metadata
        """
        try:
            query = {"user_id": user_id}
            if not include_deleted:
                query["is_deleted"] = False
            
            files = list(self.collection.find(query).sort("upload_date", -1))
            for file in files:
                file["_id"] = str(file["_id"])
            return files
        except Exception as e:
            logger.error(f"Error getting files by user: {str(e)}")
            return []
    
    def update_file(self, file_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update file metadata.
        
        Args:
            file_id: File ID
            update_data: Data to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"file_id": file_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating file: {str(e)}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete file (soft delete by setting is_deleted to True).
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"file_id": file_id},
                {"$set": {"is_deleted": True}}
            )
            logger.info(f"File marked as deleted: {file_id}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
    
    def increment_verification_count(self, file_id: str) -> bool:
        """
        Increment verification count and update last verified timestamp.
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"file_id": file_id},
                {
                    "$inc": {"verification_count": 1},
                    "$set": {"last_verified": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error incrementing verification count: {str(e)}")
            return False
    
    def update_verification_status(self, file_id: str, status: str, verified: bool) -> bool:
        """
        Update verification status of a file.
        
        Args:
            file_id: File ID
            status: Verification status (verified, tampered, pending)
            verified: Whether file is verified
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"file_id": file_id},
                {
                    "$set": {
                        "verification_status": status,
                        "verified": verified,
                        "last_verified": datetime.utcnow()
                    },
                    "$inc": {"verification_count": 1}
                }
            )
            logger.info(f"Verification status updated for {file_id}: {status}")
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating verification status: {str(e)}")
            return False
    
    def file_exists(self, file_id: str) -> bool:
        """
        Check if file exists and is not deleted.
        
        Args:
            file_id: File ID
            
        Returns:
            bool: True if file exists, False otherwise
        """
        return self.collection.find_one({"file_id": file_id, "is_deleted": False}) is not None


file_repository = FileRepository()
