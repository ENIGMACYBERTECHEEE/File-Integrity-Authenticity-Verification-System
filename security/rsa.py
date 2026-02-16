"""
RSA-2048 digital signature implementation.
Handles key generation, signing, and verification.
"""
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional
import base64
from config import config


class RSAHandler:
    """RSA cryptographic operations handler."""
    
    @staticmethod
    def generate_key_pair() -> Tuple[bytes, bytes]:
        """
        Generate RSA-2048 key pair.
        
        Returns:
            Tuple[bytes, bytes]: (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=config.RSA_KEY_SIZE,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def sign_hash(hash_digest: str, private_key_pem: bytes) -> str:
        """
        Sign a hash digest using RSA private key.
        
        Args:
            hash_digest: Hexadecimal hash digest to sign
            private_key_pem: Private key in PEM format
            
        Returns:
            str: Base64-encoded signature
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        hash_bytes = bytes.fromhex(hash_digest)
        
        signature = private_key.sign(
            hash_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify_signature(hash_digest: str, signature: str, public_key_pem: bytes) -> bool:
        """
        Verify RSA signature against hash digest.
        
        Args:
            hash_digest: Hexadecimal hash digest
            signature: Base64-encoded signature
            public_key_pem: Public key in PEM format
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )
            
            hash_bytes = bytes.fromhex(hash_digest)
            signature_bytes = base64.b64decode(signature)
            
            public_key.verify(
                signature_bytes,
                hash_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def encrypt_private_key(private_key_pem: bytes, password: str) -> bytes:
        """
        Encrypt private key with password.
        
        Args:
            private_key_pem: Unencrypted private key in PEM format
            password: Password for encryption
            
        Returns:
            bytes: Encrypted private key in PEM format
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None,
            backend=default_backend()
        )
        
        encrypted_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode())
        )
        
        return encrypted_pem
    
    @staticmethod
    def decrypt_private_key(encrypted_private_key_pem: bytes, password: str) -> Optional[bytes]:
        """
        Decrypt private key with password.
        
        Args:
            encrypted_private_key_pem: Encrypted private key in PEM format
            password: Password for decryption
            
        Returns:
            Optional[bytes]: Decrypted private key in PEM format, None if decryption fails
        """
        try:
            private_key = serialization.load_pem_private_key(
                encrypted_private_key_pem,
                password=password.encode(),
                backend=default_backend()
            )
            
            decrypted_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            return decrypted_pem
        except Exception:
            return None


rsa_handler = RSAHandler()
