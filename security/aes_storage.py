"""
AES-256-GCM encryption for file storage.
Uses PBKDF2 for key derivation and authenticated encryption.
"""
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import os
from pathlib import Path
from typing import Tuple, Union
from config import config


class AESStorage:
    """AES-256-GCM encryption handler for file storage."""
    
    def __init__(self):
        """Initialize AES storage with master key."""
        self.master_key = config.MASTER_KEY.encode()
    
    def _derive_key(self, salt: bytes) -> bytes:
        """
        Derive encryption key from master key using PBKDF2.
        
        Args:
            salt: Salt for key derivation
            
        Returns:
            bytes: Derived 256-bit key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=config.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(self.master_key)
    
    def encrypt_file(self, file_path: Union[str, Path], output_path: Union[str, Path]) -> Tuple[str, bytes]:
        """
        Encrypt a file using AES-256-GCM.
        
        Args:
            file_path: Path to the file to encrypt
            output_path: Path where encrypted file will be saved
            
        Returns:
            Tuple[str, bytes]: (output_path, iv) - path to encrypted file and initialization vector
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            IOError: If encryption fails
        """
        file_path = Path(file_path)
        output_path = Path(output_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Generate random IV and salt
            iv = os.urandom(config.AES_IV_SIZE)
            salt = os.urandom(16)
            
            # Derive encryption key
            key = self._derive_key(salt)
            aesgcm = AESGCM(key)
            
            # Read and encrypt file
            with open(file_path, "rb") as f:
                plaintext = f.read()
            
            ciphertext = aesgcm.encrypt(iv, plaintext, None)
            
            # Write encrypted data: salt + IV + ciphertext (includes auth tag)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(salt)
                f.write(iv)
                f.write(ciphertext)
            
            return str(output_path), iv
        except Exception as e:
            raise IOError(f"Encryption failed: {str(e)}")
    
    def decrypt_file(self, encrypted_path: Union[str, Path], output_path: Union[str, Path]) -> str:
        """
        Decrypt a file using AES-256-GCM.
        
        Args:
            encrypted_path: Path to the encrypted file
            output_path: Path where decrypted file will be saved
            
        Returns:
            str: Path to decrypted file
            
        Raises:
            FileNotFoundError: If encrypted file doesn't exist
            IOError: If decryption fails
        """
        encrypted_path = Path(encrypted_path)
        output_path = Path(output_path)
        
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
        
        try:
            # Read encrypted file
            with open(encrypted_path, "rb") as f:
                salt = f.read(16)
                iv = f.read(config.AES_IV_SIZE)
                ciphertext = f.read()
            
            # Derive decryption key
            key = self._derive_key(salt)
            aesgcm = AESGCM(key)
            
            # Decrypt
            plaintext = aesgcm.decrypt(iv, ciphertext, None)
            
            # Write decrypted data
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(plaintext)
            
            return str(output_path)
        except Exception as e:
            raise IOError(f"Decryption failed: {str(e)}")
    
    def encrypt_bytes(self, data: bytes) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt bytes data.
        
        Args:
            data: Plaintext bytes
            
        Returns:
            Tuple[bytes, bytes, bytes]: (ciphertext, iv, salt)
        """
        iv = os.urandom(config.AES_IV_SIZE)
        salt = os.urandom(16)
        key = self._derive_key(salt)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(iv, data, None)
        return ciphertext, iv, salt
    
    def decrypt_bytes(self, ciphertext: bytes, iv: bytes, salt: bytes) -> bytes:
        """
        Decrypt bytes data.
        
        Args:
            ciphertext: Encrypted bytes
            iv: Initialization vector
            salt: Salt used for key derivation
            
        Returns:
            bytes: Decrypted plaintext
            
        Raises:
            IOError: If decryption fails
        """
        try:
            key = self._derive_key(salt)
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(iv, ciphertext, None)
            return plaintext
        except Exception as e:
            raise IOError(f"Decryption failed: {str(e)}")


aes_storage = AESStorage()
