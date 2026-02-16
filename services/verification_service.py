"""
Verification service for file integrity and authenticity checks.
"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import os
from config import config
from repositories.file_repo import file_repository
from repositories.verification_repo import verification_repository
from services.crypto_service import crypto_service
from services.audit_service import audit_service
import logging

logger = logging.getLogger(__name__)


class VerificationService:
    """Service for file verification operations."""
    
    @staticmethod
    def verify_file(file_id: str, user_id: str, username: str) -> Dict[str, Any]:
        """
        Verify file integrity and authenticity.
        
        Workflow:
        1. Validate file_id exists in DB
        2. Check user permissions
        3. Load file metadata (hash, signature, encrypted_path)
        4. Read encrypted file from storage
        5. Decrypt using AES-256-GCM
        6. Recompute SHA-256 (chunk-based)
        7. Compare: computed_hash vs stored_hash → hash_match
        8. Verify RSA signature using public key → signature_valid
        9. Determine: verified = hash_match AND signature_valid
        10. Save verification record to DB
        11. Update file.last_verified, file.verification_count
        12. Log audit event
        13. Return verification result
        
        Args:
            file_id: File ID
            user_id: User ID
            username: Username
            
        Returns:
            Dict[str, Any]: Verification result
            
        Raises:
            ValueError: If verification fails
        """
        # Step 1: Validate file exists
        file = file_repository.get_file_by_file_id(file_id)
        
        if not file:
            raise ValueError("File not found")
        
        # Step 2: Check user permissions
        if file["user_id"] != user_id:
            raise ValueError("Unauthorized access to file")
        
        try:
            # Step 3: Load file metadata
            stored_hash = file["original_hash"]
            signature = file["signature"]
            encrypted_path = file["encrypted_path"]
            
            # Step 4-5: Decrypt file
            temp_path = config.UPLOAD_DIR / f"verify_{file_id}"
            decrypted_path = crypto_service.decrypt_file(encrypted_path, str(temp_path))
            
            # Step 6: Recompute hash
            current_hash = crypto_service.hash_file(decrypted_path)
            
            # Remove temporary file
            os.remove(decrypted_path)
            
            # Step 7: Compare hashes
            hash_match = (current_hash == stored_hash)
            
            # Step 8: Verify signature
            signature_valid = crypto_service.verify_signature(
                stored_hash,
                signature,
                user_id
            )
            
            # Step 9: Determine overall verification status
            verified = hash_match and signature_valid
            tampered = not verified
            
            # Determine details
            details = {}
            if not hash_match:
                details["hash_mismatch"] = "File has been modified"
            if not signature_valid:
                details["signature_invalid"] = "Digital signature verification failed"
            
            # Step 10: Save verification record
            verification_data = {
                "file_id": file_id,
                "user_id": user_id,
                "hash_match": hash_match,
                "signature_valid": signature_valid,
                "verified": verified,
                "current_hash": current_hash,
                "expected_hash": stored_hash,
                "details": details
            }
            
            verification_id = verification_repository.create_verification(verification_data)
            
            # Step 11: Update file metadata with verification status
            status = "verified" if verified else "tampered"
            file_repository.update_verification_status(file_id, status, verified)
            
            # Step 12: Log audit event
            result_status = "success" if verified else "failure"
            audit_service.log_event(
                user_id=user_id,
                username=username,
                action="verify",
                resource_type="file",
                resource_id=file_id,
                result=result_status,
                details={
                    "filename": file["filename"],
                    "verified": verified,
                    "hash_match": hash_match,
                    "signature_valid": signature_valid
                }
            )
            
            logger.info(f"File verification completed: {file_id}, verified={verified}")
            
            # Step 13: Return result
            return {
                "file_id": file_id,
                "filename": file["filename"],
                "verified": verified,
                "verification_status": status,
                "hash_match": hash_match,
                "signature_valid": signature_valid,
                "tampered": tampered,
                "timestamp": datetime.utcnow().isoformat(),
                "details": details,
                "verification_id": verification_id
            }
        except Exception as e:
            logger.error(f"Error verifying file: {str(e)}")
            
            # Log failed verification
            audit_service.log_event(
                user_id=user_id,
                username=username,
                action="verify",
                resource_type="file",
                resource_id=file_id,
                result="error",
                details={"error": str(e)}
            )
            
            raise ValueError(f"File verification failed: {str(e)}")
    
    @staticmethod
    def verify_batch(file_ids: List[str], user_id: str, username: str) -> Dict[str, Any]:
        """
        Verify multiple files.
        
        Args:
            file_ids: List of file IDs
            user_id: User ID
            username: Username
            
        Returns:
            Dict[str, Any]: Batch verification results
        """
        results = []
        successful = 0
        failed = 0
        
        for file_id in file_ids:
            try:
                result = VerificationService.verify_file(file_id, user_id, username)
                results.append(result)
                
                if result["verified"]:
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                results.append({
                    "file_id": file_id,
                    "verified": False,
                    "error": str(e)
                })
                failed += 1
        
        return {
            "total": len(file_ids),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    @staticmethod
    def get_verification_history(file_id: str, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get verification history for a file.
        
        Args:
            file_id: File ID
            user_id: User ID
            limit: Maximum number of records to return
            
        Returns:
            List[Dict[str, Any]]: Verification history
        """
        # Check file permissions
        file = file_repository.get_file_by_file_id(file_id)
        
        if not file:
            raise ValueError("File not found")
        
        if file["user_id"] != user_id:
            raise ValueError("Unauthorized access to file")
        
        verifications = verification_repository.get_verifications_by_file(file_id, limit)
        
        result = []
        for v in verifications:
            result.append({
                "verification_id": v["_id"],
                "timestamp": v["timestamp"].isoformat() if v.get("timestamp") else None,
                "verified": v.get("verified", False),
                "hash_match": v.get("hash_match", False),
                "signature_valid": v.get("signature_valid", False),
                "details": v.get("details", {})
            })
        
        return result


verification_service = VerificationService()
