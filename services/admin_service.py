"""
Admin Service - Administrative operations and statistics.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from repositories.user_repo import user_repository
from repositories.file_repo import file_repository
from repositories.verification_repo import verification_repository
from database import MongoDB
import logging

logger = logging.getLogger(__name__)


class AdminService:
    """Service for administrative operations."""
    
    def __init__(self):
        self.database = MongoDB.get_database()
    
    def get_system_stats(self) -> Dict:
        """
        Get comprehensive system statistics.
        
        Returns:
            dict: System statistics
        """
        try:
            # Get counts
            total_users = user_repository.count()
            total_files = file_repository.count()
            total_verifications = self.database.verifications.count_documents({})
            
            # Get recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(hours=24)
            recent_uploads = self.database.files.count_documents({
                "upload_date": {"$gte": yesterday}
            })
            recent_verifications = self.database.verifications.count_documents({
                "timestamp": {"$gte": yesterday}
            })
            recent_users = self.database.users.count_documents({
                "created_at": {"$gte": yesterday}
            })
            
            # Get storage stats
            total_size = 0
            files = self.database.files.find({"is_deleted": False})
            for file in files:
                total_size += file.get("size", 0)
            
            # Get verification success rate
            total_verifs = self.database.verifications.count_documents({})
            successful_verifs = self.database.verifications.count_documents({"verified": True})
            success_rate = (successful_verifs / total_verifs * 100) if total_verifs > 0 else 0
            
            return {
                "total_users": total_users,
                "total_files": total_files,
                "total_verifications": total_verifications,
                "total_storage_bytes": total_size,
                "total_storage_mb": round(total_size / (1024 * 1024), 2),
                "recent_uploads_24h": recent_uploads,
                "recent_verifications_24h": recent_verifications,
                "recent_users_24h": recent_users,
                "verification_success_rate": round(success_rate, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            raise
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> Dict:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            dict: Users list and count
        """
        try:
            users = list(self.database.users.find({}).skip(skip).limit(limit))
            total = self.database.users.count_documents({})
            
            # Convert ObjectId to string and remove password
            for user in users:
                user["_id"] = str(user["_id"])
                user.pop("password_hash", None)
                user.pop("rsa_private_key_encrypted", None)
            
            return {
                "users": users,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error getting all users: {str(e)}")
            raise
    
    def get_all_files(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> Dict:
        """
        Get all files with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: Whether to include deleted files
            
        Returns:
            dict: Files list and count
        """
        try:
            query = {} if include_deleted else {"is_deleted": False}
            files = list(self.database.files.find(query).skip(skip).limit(limit).sort("upload_date", -1))
            total = self.database.files.count_documents(query)
            
            # Convert ObjectId to string and add user info
            for file in files:
                file["_id"] = str(file["_id"])
                # Get username
                user = self.database.users.find_one({"_id": file.get("user_id")})
                file["username"] = user.get("username", "Unknown") if user else "Unknown"
            
            return {
                "files": files,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error getting all files: {str(e)}")
            raise
    
    def get_all_verifications(self, skip: int = 0, limit: int = 100) -> Dict:
        """
        Get all verification records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            dict: Verifications list and count
        """
        try:
            verifications = list(
                self.database.verifications.find({})
                .skip(skip)
                .limit(limit)
                .sort("timestamp", -1)
            )
            total = self.database.verifications.count_documents({})
            
            # Convert ObjectId to string and enrich with file/user info
            for verif in verifications:
                verif["_id"] = str(verif["_id"])
                
                # Get file info
                file = self.database.files.find_one({"file_id": verif.get("file_id")})
                if file:
                    verif["filename"] = file.get("filename", "Unknown")
                else:
                    verif["filename"] = "Unknown"
                
                # Get username
                user = self.database.users.find_one({"_id": verif.get("user_id")})
                verif["username"] = user.get("username", "Unknown") if user else "Unknown"
            
            return {
                "verifications": verifications,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        except Exception as e:
            logger.error(f"Error getting all verifications: {str(e)}")
            raise
    
    def update_user_status(self, user_id: str, is_active: bool) -> bool:
        """
        Activate or deactivate a user.
        
        Args:
            user_id: User ID
            is_active: New active status
            
        Returns:
            bool: Success status
        """
        try:
            from bson import ObjectId
            result = self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"is_active": is_active}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user status: {str(e)}")
            raise
    
    def update_user_role(self, user_id: str, role: str) -> bool:
        """
        Update user role.
        
        Args:
            user_id: User ID
            role: New role (admin, user)
            
        Returns:
            bool: Success status
        """
        try:
            from bson import ObjectId
            if role not in ["admin", "user"]:
                raise ValueError("Invalid role. Must be 'admin' or 'user'")
            
            result = self.database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"role": role}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user role: {str(e)}")
            raise
    
    def delete_file_permanently(self, file_id: str) -> bool:
        """
        Permanently delete a file (admin only).
        
        Args:
            file_id: File ID
            
        Returns:
            bool: Success status
        """
        try:
            import os
            
            # Get file info
            file = self.database.files.find_one({"file_id": file_id})
            if not file:
                return False
            
            # Delete physical file if exists
            if file.get("encrypted_path"):
                try:
                    if os.path.exists(file["encrypted_path"]):
                        os.remove(file["encrypted_path"])
                except Exception as e:
                    logger.warning(f"Failed to delete physical file: {str(e)}")
            
            # Delete signature file if exists
            signature_path = f"storage/signatures/{file_id}.sig"
            try:
                if os.path.exists(signature_path):
                    os.remove(signature_path)
            except Exception as e:
                logger.warning(f"Failed to delete signature file: {str(e)}")
            
            # Delete from database
            self.database.files.delete_one({"file_id": file_id})
            
            # Delete related verifications
            self.database.verifications.delete_many({"file_id": file_id})
            
            logger.info(f"Admin permanently deleted file: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Error permanently deleting file: {str(e)}")
            raise
    
    def get_user_activity(self, user_id: str, days: int = 7) -> Dict:
        """
        Get user activity summary.
        
        Args:
            user_id: User ID
            days: Number of days to look back
            
        Returns:
            dict: Activity summary
        """
        try:
            from bson import ObjectId
            cutoff = datetime.utcnow() - timedelta(days=days)
            
            # Get user info
            user = self.database.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None
            
            # Count activities
            file_count = self.database.files.count_documents({
                "user_id": ObjectId(user_id),
                "is_deleted": False
            })
            
            recent_uploads = self.database.files.count_documents({
                "user_id": ObjectId(user_id),
                "upload_date": {"$gte": cutoff}
            })
            
            verification_count = self.database.verifications.count_documents({
                "user_id": ObjectId(user_id)
            })
            
            recent_verifications = self.database.verifications.count_documents({
                "user_id": ObjectId(user_id),
                "timestamp": {"$gte": cutoff}
            })
            
            # Get audit logs
            recent_logins = self.database.audit_logs.count_documents({
                "user_id": str(user_id),
                "action": "login",
                "timestamp": {"$gte": cutoff}
            })
            
            return {
                "user_id": str(user_id),
                "username": user.get("username"),
                "total_files": file_count,
                "recent_uploads": recent_uploads,
                "total_verifications": verification_count,
                "recent_verifications": recent_verifications,
                "recent_logins": recent_logins,
                "days": days
            }
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            raise
    
    def get_activity_timeline(self, hours: int = 24) -> List[Dict]:
        """
        Get system activity timeline.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            list: Timeline events
        """
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            
            events = []
            
            # Get recent uploads
            uploads = self.database.files.find({
                "upload_date": {"$gte": cutoff}
            }).sort("upload_date", -1).limit(50)
            
            for upload in uploads:
                user = self.database.users.find_one({"_id": upload.get("user_id")})
                events.append({
                    "type": "upload",
                    "timestamp": upload.get("upload_date"),
                    "username": user.get("username") if user else "Unknown",
                    "filename": upload.get("filename"),
                    "file_id": upload.get("file_id")
                })
            
            # Get recent verifications
            verifications = self.database.verifications.find({
                "timestamp": {"$gte": cutoff}
            }).sort("timestamp", -1).limit(50)
            
            for verif in verifications:
                file = self.database.files.find_one({"file_id": verif.get("file_id")})
                user = self.database.users.find_one({"_id": verif.get("user_id")})
                events.append({
                    "type": "verification",
                    "timestamp": verif.get("timestamp"),
                    "username": user.get("username") if user else "Unknown",
                    "filename": file.get("filename") if file else "Unknown",
                    "verified": verif.get("verified"),
                    "file_id": verif.get("file_id")
                })
            
            # Sort by timestamp
            events.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
            
            # Convert datetime to string
            for event in events:
                if isinstance(event.get("timestamp"), datetime):
                    event["timestamp"] = event["timestamp"].isoformat()
            
            return events[:50]  # Return top 50
        except Exception as e:
            logger.error(f"Error getting activity timeline: {str(e)}")
            raise


# Global service instance
admin_service = AdminService()
