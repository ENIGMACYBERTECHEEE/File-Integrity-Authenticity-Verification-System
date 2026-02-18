#!/usr/bin/env python3
"""
Test Admin Login - Verify admin credentials work correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import MongoDB, get_collection
from services.auth_service import auth_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_admin_login():
    """Test admin login credentials."""
    print("=" * 60)
    print("  Testing Admin Login")
    print("=" * 60)
    print()
    
    # Connect to database
    print("1. Connecting to database...")
    MongoDB.connect()
    print("   ✓ Database connected")
    print()
    
    # Check if admin exists
    print("2. Checking if admin user exists...")
    users_collection = get_collection('users')
    admin = users_collection.find_one({'username': 'admin'})
    
    if admin:
        print(f"   ✓ Admin user found")
        print(f"     - Username: {admin['username']}")
        print(f"     - Email: {admin['email']}")
        print(f"     - Is Admin: {admin.get('is_admin', False)}")
        print(f"     - Is Active: {admin.get('is_active', False)}")
    else:
        print("   ✗ Admin user not found!")
        print("\n   Run 'python setup_users.py' to create admin user")
        return False
    print()
    
    # Test login with default credentials
    print("3. Testing login with credentials: admin / admin123")
    try:
        result = auth_service.login_user('admin', 'admin123')
        print("   ✓ Login successful!")
        print(f"     - Token generated: {result['access_token'][:50]}...")
        print(f"     - Username: {result['username']}")
        print(f"     - Email: {result['email']}")
        print(f"     - Is Admin: {result['is_admin']}")
        print()
        print("=" * 60)
        print("  ✓ ALL TESTS PASSED")
        print("=" * 60)
        print()
        print("You can now login with:")
        print("  Username: admin")
        print("  Password: admin123")
        print()
        return True
        
    except Exception as e:
        print(f"   ✗ Login failed: {e}")
        print()
        print("=" * 60)
        print("  ✗ TEST FAILED")
        print("=" * 60)
        print()
        print("Possible solutions:")
        print("1. Reset admin password: python reset_admin_password.py")
        print("2. Create new admin: python create_admin.py")
        print("3. Reinitialize users: python setup_users.py")
        print()
        return False


if __name__ == "__main__":
    try:
        success = test_admin_login()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n✗ Unexpected error: {str(e)}")
        sys.exit(1)
