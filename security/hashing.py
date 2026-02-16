"""
SHA-256 hashing implementation with chunk-based processing for large files.
"""
import hashlib
from pathlib import Path
from typing import Union, BinaryIO
from config import config


def compute_file_hash(file_path: Union[str, Path]) -> str:
    """
    Compute SHA-256 hash of a file using chunk-based reading.
    
    Args:
        file_path: Path to the file to hash
        
    Returns:
        str: Hexadecimal digest of the file hash
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    sha256_hash = hashlib.sha256()
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(config.CHUNK_SIZE), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        raise IOError(f"Error reading file for hashing: {str(e)}")


def compute_bytes_hash(data: bytes) -> str:
    """
    Compute SHA-256 hash of bytes data.
    
    Args:
        data: Bytes data to hash
        
    Returns:
        str: Hexadecimal digest of the hash
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    return sha256_hash.hexdigest()


def compute_stream_hash(stream: BinaryIO) -> str:
    """
    Compute SHA-256 hash of a binary stream using chunk-based reading.
    
    Args:
        stream: Binary stream to hash
        
    Returns:
        str: Hexadecimal digest of the hash
    """
    sha256_hash = hashlib.sha256()
    stream.seek(0)
    for chunk in iter(lambda: stream.read(config.CHUNK_SIZE), b""):
        sha256_hash.update(chunk)
    stream.seek(0)
    return sha256_hash.hexdigest()


def verify_hash(file_path: Union[str, Path], expected_hash: str) -> bool:
    """
    Verify if a file's hash matches the expected hash.
    
    Args:
        file_path: Path to the file to verify
        expected_hash: Expected hash value
        
    Returns:
        bool: True if hashes match, False otherwise
    """
    try:
        actual_hash = compute_file_hash(file_path)
        return actual_hash == expected_hash
    except Exception:
        return False
