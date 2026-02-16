"""
Cryptographic service for hashing, signing, and encryption operations.
"""
from typing import Tuple, Optional
from pathlib import Path
from security.hashing import compute_file_hash, compute_bytes_hash, compute_stream_hash
from security.rsa import rsa_handler
from security.aes_storage import aes_storage
from repositories.key_repo import key_repository
import logging

logger = logging.getLogger(__name__)


class CryptoService:
    """Service for cryptographic operations."""
    
    @staticmethod
    def hash_file(file_path: str) -> str:
        """
        Compute SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Hexadecimal hash digest
        """
        try:
            return compute_file_hash(file_path)
        except Exception as e:
            logger.error(f"Error hashing file: {str(e)}")
            raise
    
    @staticmethod
    def hash_bytes(data: bytes) -> str:
        """
        Compute SHA-256 hash of bytes.
        
        Args:
            data: Bytes data
            
        Returns:
            str: Hexadecimal hash digest
        """
        return compute_bytes_hash(data)
    
    @staticmethod
    def sign_file_hash(file_hash: str, user_id: str, password: str) -> Optional[str]:
        """
        Sign a file hash using user's private key.
        
        Args:
            file_hash: File hash to sign
            user_id: User ID
            password: User's password to decrypt private key
            
        Returns:
            Optional[str]: Base64-encoded signature or None if signing fails
        """
        try:
            # Get encrypted private key
            encrypted_private_key = key_repository.get_encrypted_private_key(user_id)
            
            if not encrypted_private_key:
                logger.error(f"Private key not found for user: {user_id}")
                return None
            
            # Decrypt private key
            private_key_pem = rsa_handler.decrypt_private_key(
                encrypted_private_key.encode('utf-8'),
                password
            )
            
            if not private_key_pem:
                logger.error("Failed to decrypt private key")
                return None
            
            # Sign the hash
            signature = rsa_handler.sign_hash(file_hash, private_key_pem)
            return signature
        except Exception as e:
            logger.error(f"Error signing file hash: {str(e)}")
            return None
    
    @staticmethod
    def verify_signature(file_hash: str, signature: str, user_id: str) -> bool:
        """
        Verify a signature against a file hash.
        
        Args:
            file_hash: File hash
            signature: Base64-encoded signature
            user_id: User ID
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Get public key
            public_key = key_repository.get_public_key(user_id)
            
            if not public_key:
                logger.error(f"Public key not found for user: {user_id}")
                return False
            
            # Verify signature
            is_valid = rsa_handler.verify_signature(
                file_hash,
                signature,
                public_key.encode('utf-8')
            )
            return is_valid
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False
    
    @staticmethod
    def encrypt_file(input_path: str, output_path: str) -> Tuple[str, bytes]:
        """
        Encrypt a file using AES-256-GCM.
        
        Args:
            input_path: Path to the file to encrypt
            output_path: Path where encrypted file will be saved
            
        Returns:
            Tuple[str, bytes]: (encrypted_file_path, iv)
        """
        try:
            encrypted_path, iv = aes_storage.encrypt_file(input_path, output_path)
            return encrypted_path, iv
        except Exception as e:
            logger.error(f"Error encrypting file: {str(e)}")
            raise
    
    @staticmethod
    def decrypt_file(encrypted_path: str, output_path: str) -> str:
        """
        Decrypt a file using AES-256-GCM.
        
        Args:
            encrypted_path: Path to the encrypted file
            output_path: Path where decrypted file will be saved
            
        Returns:
            str: Path to decrypted file
        """
        try:
            decrypted_path = aes_storage.decrypt_file(encrypted_path, output_path)
            return decrypted_path
        except Exception as e:
            logger.error(f"Error decrypting file: {str(e)}")
            raise
    
    @staticmethod
    def generate_key_pair() -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair.
        
        Returns:
            Tuple[bytes, bytes]: (private_key_pem, public_key_pem)
        """
        return rsa_handler.generate_key_pair()


crypto_service = CryptoService()
