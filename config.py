"""
Configuration management for the File Integrity & Authenticity Verification Platform.
Loads configuration from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Application configuration."""
    
    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "file_integrity_db")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production-12345")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    
    # Security Configuration
    MASTER_KEY: str = os.getenv("MASTER_KEY", "master-encryption-key-32bytes!!")
    RSA_KEY_SIZE: int = int(os.getenv("RSA_KEY_SIZE", "2048"))
    PASSWORD_MIN_LENGTH: int = 8
    
    # Storage Configuration
    UPLOAD_DIR: Path = BASE_DIR / os.getenv("UPLOAD_DIR", "storage/files")
    SIGNATURE_DIR: Path = BASE_DIR / os.getenv("SIGNATURE_DIR", "storage/signatures")
    KEY_DIR: Path = BASE_DIR / os.getenv("KEY_DIR", "storage/keys")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = BASE_DIR / os.getenv("LOG_FILE", "logs/app.log")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    
    # Message Queue (RabbitMQ)
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://admin:admin123@localhost:5672//")
    
    # File Upload Limits
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    
    # Cryptography
    CHUNK_SIZE: int = 8192
    PBKDF2_ITERATIONS: int = 100000
    AES_IV_SIZE: int = 12
    
    @classmethod
    def ensure_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.SIGNATURE_DIR.mkdir(parents=True, exist_ok=True)
        cls.KEY_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


config = Config()
