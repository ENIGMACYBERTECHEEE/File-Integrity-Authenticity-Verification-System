#!/usr/bin/env python3
"""
Reset Admin Password - File Integrity & Authenticity Verification Platform
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import MongoDB, get_collection
from services.auth_service import auth_service
from security.rsa import rsa_handler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_admin_password():
    """Reset the admin user password."""
    print("=" * 60)
    print("  File Integrity Platform - Reset Admin Password")
    print("=" * 60)
    print()
    
    # Connect to database
    MongoDB.connect()
    users_collection = get_collection('users')
    keys_collection = get_collection('keys')
    
    # Find admin user
    admin = users_collection.find_one({'username': 'admin'})
    
    if not admin:
        print("❌ Admin user not found!")
        print("\nCreating a new admin user instead...")
        
        # Create new admin
        admin_username = input("Enter admin username (default: admin): ").strip() or "admin"
        admin_email = input("Enter admin email (default: admin@test.com): ").strip() or "admin@test.com"
        admin_password = input("Enter admin password (min 8 chars): ").strip()
        
        if len(admin_password) < 8:
            print("❌ Password must be at least 8 characters!")
            return
        
        # Hash password
        hashed_password = auth_service.hash_password(admin_password)
        
        # Generate RSA keys
        private_key_pem, public_key_pem = rsa_handler.generate_key_pair()
        encrypted_private_key = rsa_handler.encrypt_private_key(private_key_pem, admin_password)
        
        # Create admin user
        user_data = {
            'username': admin_username,
            'email': admin_email,
            'password_hash': hashed_password,
            'is_active': True,
            'is_admin': True,
            'role': 'admin'
        }
        
        result = users_collection.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        # Store keys
        key_data = {
            'user_id': user_id,
            'public_key': public_key_pem.decode('utf-8'),
            'encrypted_private_key': encrypted_private_key.decode('utf-8')
        }
        keys_collection.insert_one(key_data)
        
        print(f"\n✓ Admin user created successfully!")
        print(f"  Username: {admin_username}")
        print(f"  Email: {admin_email}")
        print(f"  Password: {admin_password}")
        return
    
    print(f"Found admin user: {admin['username']} ({admin['email']})")
    print()
    
    # Get new password
    new_password = input("Enter new password (min 8 chars): ").strip()
    
    if len(new_password) < 8:
        print("❌ Password must be at least 8 characters!")
        return
    
    confirm_password = input("Confirm new password: ").strip()
    
    if new_password != confirm_password:
        print("❌ Passwords do not match!")
        return
    
    try:
        # Hash new password
        hashed_password = auth_service.hash_password(new_password)
        
        # Update password
        users_collection.update_one(
            {'_id': admin['_id']},
            {'$set': {'password_hash': hashed_password}}
        )
        
        # Update RSA keys with new password
        admin_id = str(admin['_id'])
        
        # Generate new RSA keys
        private_key_pem, public_key_pem = rsa_handler.generate_key_pair()
        encrypted_private_key = rsa_handler.encrypt_private_key(private_key_pem, new_password)
        
        # Update keys
        keys_collection.update_one(
            {'user_id': admin_id},
            {
                '$set': {
                    'public_key': public_key_pem.decode('utf-8'),
                    'encrypted_private_key': encrypted_private_key.decode('utf-8')
                }
            },
            upsert=True
        )
        
        print("\n✓ Admin password reset successfully!")
        print(f"  Username: {admin['username']}")
        print(f"  New Password: {new_password}")
        print("\n⚠️  Please update your credentials and login again.")
        
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        print(f"\n❌ Error resetting password: {str(e)}")


if __name__ == "__main__":
    try:
        reset_admin_password()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
