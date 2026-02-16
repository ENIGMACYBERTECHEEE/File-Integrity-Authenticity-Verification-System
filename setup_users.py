#!/usr/bin/env python3
import sys
sys.path.insert(0, '/app')
from database import MongoDB
from services.auth_service import auth_service
from repositories.user_repo import user_repository
from repositories.key_repo import key_repository
from security.rsa import rsa_handler

MongoDB.connect()

# Create admin user
admin_username = 'admin'
admin_email = 'admin@test.com'
admin_password = 'admin123'

if not user_repository.user_exists(admin_username, admin_email):
    hashed_password = auth_service.hash_password(admin_password)
    private_key_pem, public_key_pem = rsa_handler.generate_key_pair()
    encrypted_private_key = rsa_handler.encrypt_private_key(private_key_pem, admin_password)
    
    user_data = {
        'username': admin_username,
        'email': admin_email,
        'password_hash': hashed_password,
        'is_active': True,
        'is_admin': True
    }
    
    user_id = user_repository.create_user(user_data)
    key_repository.store_keys(user_id, public_key_pem, encrypted_private_key)
    print('✓ Admin created: admin / admin123')
else:
    print('Admin already exists')

# Create test user
test_username = 'testuser'
test_email = 'test@test.com'
test_password = 'testpass123'

if not user_repository.user_exists(test_username, test_email):
    hashed_password = auth_service.hash_password(test_password)
    private_key_pem, public_key_pem = rsa_handler.generate_key_pair()
    encrypted_private_key = rsa_handler.encrypt_private_key(private_key_pem, test_password)
    
    user_data = {
        'username': test_username,
        'email': test_email,
        'password_hash': hashed_password,
        'is_active': True,
        'is_admin': False
    }
    
    user_id = user_repository.create_user(user_data)
    key_repository.store_keys(user_id, public_key_pem, encrypted_private_key)
    print('✓ Test user created: testuser / testpass123')
else:
    print('Test user already exists')
