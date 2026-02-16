"""
File service for file upload, download, and management operations.
"""
from typing import Dict, Any, List, BinaryIO, Optional
from pathlib import Path
import uuid
import os
from datetime import datetime
from config import config
from repositories.file_repo import file_repository
from services.crypto_service import crypto_service
from services.audit_service import audit_service
import logging

logger = logging.getLogger(__name__)


class FileService:
    """Service for file operations."""
    
    @staticmethod
    def upload_file(
        file_content: bytes,
        filename: str,
        user_id: str,
        username: str,
        password: str,
        description: str = None,
        mime_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        """
        Upload and encrypt a file.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            user_id: User ID
            username: Username
            password: User's password for signing
            description: Optional file description
            mime_type: MIME type of the file
            
        Returns:
            Dict[str, Any]: Upload result with file metadata
            
        Raises:
            ValueError: If upload fails
        """
        # Validate file size
        file_size = len(file_content)
        if file_size > config.MAX_FILE_SIZE_BYTES:
            raise ValueError(f"File size exceeds maximum limit of {config.MAX_FILE_SIZE_MB}MB")
        
        if file_size == 0:
            raise ValueError("Cannot upload empty file")
        
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Save file temporarily
            temp_path = config.UPLOAD_DIR / f"temp_{file_id}"
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(file_content)
            
            # Compute hash
            file_hash = crypto_service.hash_file(str(temp_path))
            
            # Sign the hash
            signature = crypto_service.sign_file_hash(file_hash, user_id, password)
            if not signature:
                os.remove(temp_path)
                raise ValueError("Failed to sign file. Check your password.")
            
            # Encrypt file
            encrypted_path = config.UPLOAD_DIR / f"{file_id}.enc"
            crypto_service.encrypt_file(str(temp_path), str(encrypted_path))
            
            # Remove temporary file
            os.remove(temp_path)
            
            # Store file metadata
            file_data = {
                "file_id": file_id,
                "user_id": user_id,
                "filename": filename,
                "original_hash": file_hash,
                "signature": signature,
                "encrypted_path": str(encrypted_path),
                "size": file_size,
                "metadata": {
                    "mime_type": mime_type,
                    "description": description
                }
            }
            
            record_id = file_repository.create_file(file_data)
            
            # Log audit event
            audit_service.log_event(
                user_id=user_id,
                username=username,
                action="upload",
                resource_type="file",
                resource_id=file_id,
                result="success",
                details={
                    "filename": filename,
                    "size": file_size,
                    "hash": file_hash
                }
            )
            
            logger.info(f"File uploaded successfully: {file_id}")
            
            return {
                "file_id": file_id,
                "filename": filename,
                "size": file_size,
                "hash": file_hash,
                "upload_date": datetime.utcnow().isoformat(),
                "message": "File uploaded successfully"
            }
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            # Clean up on error
            if temp_path.exists():
                os.remove(temp_path)
            raise ValueError(f"File upload failed: {str(e)}")
    
    @staticmethod
    def download_file(file_id: str, user_id: str, username: str) -> Dict[str, Any]:
        """
        Download and decrypt a file.
        
        Args:
            file_id: File ID
            user_id: User ID
            username: Username
            
        Returns:
            Dict[str, Any]: Download result with file content and metadata
            
        Raises:
            ValueError: If download fails
        """
        # Get file metadata
        file = file_repository.get_file_by_file_id(file_id)
        
        if not file:
            raise ValueError("File not found")
        
        # Check permissions
        if file["user_id"] != user_id:
            raise ValueError("Unauthorized access to file")
        
        try:
            # Decrypt file
            temp_path = config.UPLOAD_DIR / f"download_{file_id}"
            decrypted_path = crypto_service.decrypt_file(
                file["encrypted_path"],
                str(temp_path)
            )
            
            # Read decrypted content
            with open(decrypted_path, "rb") as f:
                file_content = f.read()
            
            # Remove temporary file
            os.remove(decrypted_path)
            
            # Log audit event
            audit_service.log_event(
                user_id=user_id,
                username=username,
                action="download",
                resource_type="file",
                resource_id=file_id,
                result="success",
                details={"filename": file["filename"]}
            )
            
            logger.info(f"File downloaded successfully: {file_id}")
            
            return {
                "file_content": file_content,
                "filename": file["filename"],
                "mime_type": file["metadata"].get("mime_type", "application/octet-stream"),
                "size": file["size"]
            }
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise ValueError(f"File download failed: {str(e)}")
    
    @staticmethod
    def delete_file(file_id: str, user_id: str, username: str) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            file_id: File ID
            user_id: User ID
            username: Username
            
        Returns:
            Dict[str, Any]: Deletion result
            
        Raises:
            ValueError: If deletion fails
        """
        # Get file metadata
        file = file_repository.get_file_by_file_id(file_id)
        
        if not file:
            raise ValueError("File not found")
        
        # Check permissions
        if file["user_id"] != user_id:
            raise ValueError("Unauthorized access to file")
        
        try:
            # Soft delete in database
            success = file_repository.delete_file(file_id)
            
            if not success:
                raise ValueError("Failed to delete file")
            
            # Optionally remove encrypted file from storage
            encrypted_path = Path(file["encrypted_path"])
            if encrypted_path.exists():
                os.remove(encrypted_path)
            
            # Log audit event
            audit_service.log_event(
                user_id=user_id,
                username=username,
                action="delete",
                resource_type="file",
                resource_id=file_id,
                result="success",
                details={"filename": file["filename"]}
            )
            
            logger.info(f"File deleted successfully: {file_id}")
            
            return {
                "file_id": file_id,
                "message": "File deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise ValueError(f"File deletion failed: {str(e)}")
    
    @staticmethod
    def get_file_metadata(file_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get file metadata.
        
        Args:
            file_id: File ID
            user_id: User ID
            
        Returns:
            Dict[str, Any]: File metadata
            
        Raises:
            ValueError: If file not found or unauthorized
        """
        file = file_repository.get_file_by_file_id(file_id)
        
        if not file:
            raise ValueError("File not found")
        
        if file["user_id"] != user_id:
            raise ValueError("Unauthorized access to file")
        
        return {
            "file_id": file["file_id"],
            "filename": file["filename"],
            "size": file["size"],
            "hash": file["original_hash"],
            "upload_date": file["upload_date"].isoformat() if file.get("upload_date") else None,
            "last_verified": file["last_verified"].isoformat() if file.get("last_verified") else None,
            "verification_count": file.get("verification_count", 0),
            "description": file["metadata"].get("description"),
            "mime_type": file["metadata"].get("mime_type")
        }
    
    @staticmethod
    def list_user_files(user_id: str) -> List[Dict[str, Any]]:
        """
        List all files for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List[Dict[str, Any]]: List of file metadata
        """
        files = file_repository.get_files_by_user(user_id)
        
        result = []
        for file in files:
            result.append({
                "file_id": file["file_id"],
                "filename": file["filename"],
                "file_hash": file.get("original_hash", ""),
                "size": file["size"],
                "upload_date": file["upload_date"].isoformat() if file.get("upload_date") else None,
                "last_verified": file["last_verified"].isoformat() if file.get("last_verified") else None,
                "verification_count": file.get("verification_count", 0),
                "verification_status": file.get("verification_status", "pending"),
                "description": file.get("metadata", {}).get("description", "") if file.get("metadata") else ""
            })
        
        return result


file_service = FileService()
