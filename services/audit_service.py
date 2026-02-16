"""
Audit service for logging and monitoring system activities.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from database import get_collection
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging and monitoring."""
    
    def __init__(self):
        """Initialize audit service."""
        self.collection = get_collection("audit_logs")
    
    def log_event(
        self,
        user_id: str,
        username: str,
        action: str,
        resource_type: str = None,
        resource_id: str = None,
        result: str = "success",
        ip_address: str = None,
        details: Dict[str, Any] = None
    ) -> str:
        """
        Log an audit event.
        
        Args:
            user_id: User ID
            username: Username
            action: Action performed (upload, verify, download, delete, login, etc.)
            resource_type: Type of resource (file, user, etc.)
            resource_id: ID of the resource
            result: Result of the action (success, failure, error)
            ip_address: IP address of the user
            details: Additional details
            
        Returns:
            str: Audit log ID
        """
        try:
            log_entry = {
                "timestamp": datetime.utcnow(),
                "user_id": user_id,
                "username": username,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "result": result,
                "ip_address": ip_address,
                "details": details or {}
            }
            
            result = self.collection.insert_one(log_entry)
            logger.info(f"Audit log created: {action} by {username}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            raise ValueError(f"Failed to create audit log: {str(e)}")
    
    def get_logs(
        self,
        user_id: str = None,
        action: str = None,
        from_date: datetime = None,
        to_date: datetime = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs with filters.
        
        Args:
            user_id: Filter by user ID
            action: Filter by action
            from_date: Filter by start date
            to_date: Filter by end date
            limit: Maximum number of logs to return
            
        Returns:
            List[Dict[str, Any]]: List of audit logs
        """
        try:
            query = {}
            
            if user_id:
                query["user_id"] = user_id
            
            if action:
                query["action"] = action
            
            if from_date or to_date:
                timestamp_query = {}
                if from_date:
                    timestamp_query["$gte"] = from_date
                if to_date:
                    timestamp_query["$lte"] = to_date
                query["timestamp"] = timestamp_query
            
            logs = list(
                self.collection.find(query)
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            for log in logs:
                log["_id"] = str(log["_id"])
            
            return logs
        except Exception as e:
            logger.error(f"Error querying audit logs: {str(e)}")
            return []
    
    def get_user_activity(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user activity history.
        
        Args:
            user_id: User ID
            limit: Maximum number of logs to return
            
        Returns:
            List[Dict[str, Any]]: List of user activity logs
        """
        return self.get_logs(user_id=user_id, limit=limit)
    
    def get_failed_verifications(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get failed verification attempts.
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List[Dict[str, Any]]: List of failed verification logs
        """
        try:
            logs = list(
                self.collection.find({
                    "action": "verify",
                    "result": "failure"
                })
                .sort("timestamp", -1)
                .limit(limit)
            )
            
            for log in logs:
                log["_id"] = str(log["_id"])
            
            return logs
        except Exception as e:
            logger.error(f"Error getting failed verifications: {str(e)}")
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dict[str, Any]: System statistics
        """
        try:
            total_logs = self.collection.count_documents({})
            
            upload_count = self.collection.count_documents({"action": "upload"})
            verify_count = self.collection.count_documents({"action": "verify"})
            download_count = self.collection.count_documents({"action": "download"})
            delete_count = self.collection.count_documents({"action": "delete"})
            
            failed_verifications = self.collection.count_documents({
                "action": "verify",
                "result": "failure"
            })
            
            return {
                "total_logs": total_logs,
                "upload_count": upload_count,
                "verify_count": verify_count,
                "download_count": download_count,
                "delete_count": delete_count,
                "failed_verifications": failed_verifications
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {str(e)}")
            return {}


audit_service = AuditService()
