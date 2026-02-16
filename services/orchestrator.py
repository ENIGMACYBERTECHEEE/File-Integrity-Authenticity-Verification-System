"""
Service orchestrator for coordinating multi-service workflows.
"""
from typing import Dict, Any, BinaryIO
from services.auth_service import auth_service
from services.file_service import file_service
from services.crypto_service import crypto_service
from services.verification_service import verification_service
from services.audit_service import audit_service
import logging

logger = logging.getLogger(__name__)


class ServiceOrchestrator:
    """Orchestrator for coordinating multiple services."""
    
    @staticmethod
    def register_and_setup_user(username: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register user and set up all necessary components.
        
        Args:
            username: Username
            email: Email address
            password: Password
            
        Returns:
            Dict[str, Any]: Registration result
        """
        try:
            result = auth_service.register_user(username, email, password)
            
            # Log registration
            audit_service.log_event(
                user_id=result["user_id"],
                username=username,
                action="register",
                resource_type="user",
                resource_id=result["user_id"],
                result="success",
                details={"email": email}
            )
            
            logger.info(f"User registration completed: {username}")
            return result
        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(username: str, password: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Authenticate user and log the event.
        
        Args:
            username: Username
            password: Password
            ip_address: IP address
            
        Returns:
            Dict[str, Any]: Authentication result with token
        """
        try:
            result = auth_service.login_user(username, password)
            
            # Log login
            audit_service.log_event(
                user_id=result["user_id"],
                username=username,
                action="login",
                resource_type="user",
                resource_id=result["user_id"],
                result="success",
                ip_address=ip_address,
                details={"email": result["email"]}
            )
            
            logger.info(f"User authentication completed: {username}")
            return result
        except Exception as e:
            logger.error(f"User authentication failed: {str(e)}")
            raise
    
    @staticmethod
    def upload_and_verify_file(
        file_content: bytes,
        filename: str,
        user_id: str,
        username: str,
        password: str,
        description: str = None,
        mime_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        Upload file and perform initial verification.
        
        Args:
            file_content: File content
            filename: Filename
            user_id: User ID
            username: Username
            password: User password for signing
            description: File description
            mime_type: MIME type
            
        Returns:
            Dict[str, Any]: Upload and verification result
        """
        try:
            # Upload file
            upload_result = file_service.upload_file(
                file_content=file_content,
                filename=filename,
                user_id=user_id,
                username=username,
                password=password,
                description=description,
                mime_type=mime_type
            )
            
            logger.info(f"File upload orchestration completed: {upload_result['file_id']}")
            return upload_result
        except Exception as e:
            logger.error(f"File upload orchestration failed: {str(e)}")
            raise
    
    @staticmethod
    def verify_and_audit_file(file_id: str, user_id: str, username: str) -> Dict[str, Any]:
        """
        Verify file and ensure audit logging.
        
        Args:
            file_id: File ID
            user_id: User ID
            username: Username
            
        Returns:
            Dict[str, Any]: Verification result
        """
        try:
            result = verification_service.verify_file(file_id, user_id, username)
            logger.info(f"File verification orchestration completed: {file_id}")
            return result
        except Exception as e:
            logger.error(f"File verification orchestration failed: {str(e)}")
            raise
    
    @staticmethod
    def get_user_dashboard(user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive user dashboard data.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Dashboard data
        """
        try:
            # Get user files
            files = file_service.list_user_files(user_id)
            
            # Get recent activity
            activity = audit_service.get_user_activity(user_id, limit=20)
            
            # Calculate statistics
            total_files = len(files)
            total_verifications = sum(f.get("verification_count", 0) for f in files)
            
            return {
                "total_files": total_files,
                "total_verifications": total_verifications,
                "files": files,
                "recent_activity": activity
            }
        except Exception as e:
            logger.error(f"Error getting user dashboard: {str(e)}")
            raise


service_orchestrator = ServiceOrchestrator()
