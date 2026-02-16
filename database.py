"""
MongoDB database connection and management.
"""
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from pymongo.collection import Collection
from config import config
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB connection manager."""
    
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None
    
    @classmethod
    def connect(cls) -> Database:
        """
        Establish connection to MongoDB and return database instance.
        
        Returns:
            Database: MongoDB database instance
        """
        if cls._client is None:
            try:
                cls._client = MongoClient(config.MONGO_URI)
                cls._db = cls._client[config.DATABASE_NAME]
                cls._create_indexes()
                logger.info(f"Connected to MongoDB database: {config.DATABASE_NAME}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise
        return cls._db
    
    @classmethod
    def disconnect(cls) -> None:
        """Close MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._db = None
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    def get_database(cls) -> Database:
        """
        Get database instance, connecting if necessary.
        
        Returns:
            Database: MongoDB database instance
        """
        if cls._db is None:
            return cls.connect()
        return cls._db
    
    @classmethod
    def _create_indexes(cls) -> None:
        """Create necessary database indexes for performance."""
        try:
            db = cls._db
            
            # Users collection indexes
            db.users.create_index([("username", ASCENDING)], unique=True)
            db.users.create_index([("email", ASCENDING)], unique=True)
            
            # Files collection indexes
            db.files.create_index([("file_id", ASCENDING)], unique=True)
            db.files.create_index([("user_id", ASCENDING)])
            db.files.create_index([("upload_date", ASCENDING)])
            db.files.create_index([("is_deleted", ASCENDING)])
            
            # Verifications collection indexes
            db.verifications.create_index([("file_id", ASCENDING)])
            db.verifications.create_index([("user_id", ASCENDING)])
            db.verifications.create_index([("timestamp", ASCENDING)])
            
            # Audit logs collection indexes
            db.audit_logs.create_index([("user_id", ASCENDING)])
            db.audit_logs.create_index([("timestamp", ASCENDING)])
            db.audit_logs.create_index([("action", ASCENDING)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {str(e)}")


def get_collection(collection_name: str) -> Collection:
    """
    Get a MongoDB collection by name.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection: MongoDB collection instance
    """
    db = MongoDB.get_database()
    return db[collection_name]
