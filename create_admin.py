#!/usr/bin/env python3
"""
Create Admin User for File Integrity & Authenticity Verification Platform
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import MongoDB
from services.auth_service import auth_service
from repositories.user_repo import user_repository
from repositories.key_repo import key_repository
from security.rsa import rsa_handler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user():
    """Create the admin user."""
    print("=" * 60)
    print("  File Integrity Platform - Admin User Creation")
    print("=" * 60)
    print()
    
    # Connect to database
    MongoDB.connect()
    
    # Admin credentials
    admin_username = input("Enter admin username (default: admin): ").strip() or "admin"
    admin_email = input("Enter admin email (default: admin@fileintegrity.local): ").strip() or "admin@fileintegrity.local"
    admin_password = input("Enter admin password (min 8 chars): ").strip()
    
    if len(admin_password) < 8:
        print("❌ Password must be at least 8 characters!")
        return
    
    # Check if admin already exists
    if user_repository.user_exists(admin_username, admin_email):
        print(f"❌ User '{admin_username}' or email '{admin_email}' already exists!")
        return
    
    try:
        # Hash password
        hashed_password = auth_service.hash_password(admin_password)
        
        # Generate RSA keys
        private_key_pem, public_key_pem = rsa_handler.generate_key_pair()
        encrypted_private_key = rsa_handler.encrypt_private_key(private_key_pem, admin_password)
        
        # Create admin user with is_admin flag
        user_data = {
            "username": admin_username,
            "email": admin_email,
            "password_hash": hashed_password,
            "is_admin": True,  # Admin flag
            "role": "admin"
        }
        
        user_id = user_repository.create_user(user_data)
        
        # Store keys
        key_repository.store_keys(
            user_id=user_id,
            public_key=public_key_pem,
            encrypted_private_key=encrypted_private_key
        )
        
        print()
        print("✅ Admin user created successfully!")
        print()
        print(f"Username: {admin_username}")
        print(f"Email: {admin_email}")
        print(f"Role: Administrator")
        print()
        print("You can now login at: http://localhost:3000")
        print()
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        logger.error(f"Admin creation failed: {e}", exc_info=True)
    finally:
        MongoDB.disconnect()


if __name__ == "__main__":
    create_admin_user()
