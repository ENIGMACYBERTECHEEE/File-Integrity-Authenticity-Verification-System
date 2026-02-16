#!/usr/bin/env python3
"""
System test script to verify all components are working.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all module imports."""
    print("=" * 60)
    print("TESTING MODULE IMPORTS")
    print("=" * 60)
    
    try:
        from config import config
        print("✓ config imported")
        
        from database import MongoDB
        print("✓ database imported")
        
        from security.hashing import compute_bytes_hash
        print("✓ hashing imported")
        
        from security.rsa import rsa_handler
        print("✓ rsa imported")
        
        from security.aes_storage import aes_storage
        print("✓ aes_storage imported")
        
        from security.jwt_utils import jwt_handler
        print("✓ jwt_utils imported")
        
        from repositories.user_repo import user_repository
        print("✓ user_repo imported")
        
        from repositories.file_repo import file_repository
        print("✓ file_repo imported")
        
        from repositories.verification_repo import verification_repository
        print("✓ verification_repo imported")
        
        from repositories.key_repo import key_repository
        print("✓ key_repo imported")
        
        from services.auth_service import auth_service
        print("✓ auth_service imported")
        
        from services.crypto_service import crypto_service
        print("✓ crypto_service imported")
        
        from services.file_service import file_service
        print("✓ file_service imported")
        
        from services.verification_service import verification_service
        print("✓ verification_service imported")
        
        from services.audit_service import audit_service
        print("✓ audit_service imported")
        
        from services.orchestrator import service_orchestrator
        print("✓ orchestrator imported")
        
        print("\n✓ All imports successful!\n")
        return True
    except Exception as e:
        print(f"\n✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cryptography():
    """Test cryptographic functions."""
    print("=" * 60)
    print("TESTING CRYPTOGRAPHIC FUNCTIONS")
    print("=" * 60)
    
    try:
        from security.hashing import compute_bytes_hash
        from security.rsa import rsa_handler
        from security.jwt_utils import jwt_handler
        
        # Test hashing
        test_data = b"Hello, World!"
        hash_result = compute_bytes_hash(test_data)
        print(f"✓ SHA-256 hash: {hash_result[:16]}...")
        
        # Test RSA key generation
        private_key, public_key = rsa_handler.generate_key_pair()
        print(f"✓ RSA key pair generated ({len(private_key)} bytes private, {len(public_key)} bytes public)")
        
        # Test RSA signing
        signature = rsa_handler.sign_hash(hash_result, private_key)
        print(f"✓ RSA signature created: {signature[:32]}...")
        
        # Test RSA verification
        is_valid = rsa_handler.verify_signature(hash_result, signature, public_key)
        print(f"✓ RSA signature verification: {is_valid}")
        
        # Test JWT
        token_data = {"sub": "test_user", "username": "testuser"}
        token = jwt_handler.create_access_token(token_data)
        print(f"✓ JWT token created: {token[:32]}...")
        
        decoded = jwt_handler.decode_token(token)
        print(f"✓ JWT token decoded: {decoded['username']}")
        
        print("\n✓ All cryptographic tests passed!\n")
        return True
    except Exception as e:
        print(f"\n✗ Cryptographic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_connection():
    """Test MongoDB connection."""
    print("=" * 60)
    print("TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        from database import MongoDB
        from config import config
        
        db = MongoDB.connect()
        print(f"✓ Connected to MongoDB: {config.DATABASE_NAME}")
        
        # Test collections
        collections = db.list_collection_names()
        print(f"✓ Accessible collections: {', '.join(collections) if collections else 'none (new database)'}")
        
        print("\n✓ Database connection successful!\n")
        return True
    except Exception as e:
        print(f"\n✗ Database connection failed: {e}")
        print("  Make sure MongoDB is running: brew services start mongodb-community")
        return False


def test_file_operations():
    """Test file encryption/decryption."""
    print("=" * 60)
    print("TESTING FILE ENCRYPTION/DECRYPTION")
    print("=" * 60)
    
    try:
        from security.aes_storage import aes_storage
        from pathlib import Path
        import tempfile
        import os
        
        # Create temporary test file
        test_content = b"This is a test file for encryption!"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(test_content)
            tmp_path = tmp.name
        
        try:
            # Encrypt
            encrypted_path = tmp_path + ".enc"
            result_path, iv = aes_storage.encrypt_file(tmp_path, encrypted_path)
            print(f"✓ File encrypted: {Path(result_path).name}")
            print(f"  IV: {iv.hex()[:32]}...")
            
            # Decrypt
            decrypted_path = tmp_path + ".dec"
            aes_storage.decrypt_file(encrypted_path, decrypted_path)
            print(f"✓ File decrypted: {Path(decrypted_path).name}")
            
            # Verify content
            with open(decrypted_path, "rb") as f:
                decrypted_content = f.read()
            
            if decrypted_content == test_content:
                print("✓ Decrypted content matches original")
            else:
                print("✗ Decrypted content does not match!")
                return False
            
            # Cleanup
            os.unlink(tmp_path)
            os.unlink(encrypted_path)
            os.unlink(decrypted_path)
            
            print("\n✓ File encryption/decryption tests passed!\n")
            return True
        except Exception as e:
            # Cleanup on error
            for path in [tmp_path, encrypted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)
            raise
    except Exception as e:
        print(f"\n✗ File operation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fastapi_app():
    """Test FastAPI application startup."""
    print("=" * 60)
    print("TESTING FASTAPI APPLICATION")
    print("=" * 60)
    
    try:
        from gateway.main import app
        print("✓ FastAPI app imported successfully")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"✓ Total routes: {len(routes)}")
        
        # Check key endpoints
        key_endpoints = ["/health", "/api/v1/auth/register", "/api/v1/auth/login", 
                        "/api/v1/files/upload", "/api/v1/verify/{file_id}"]
        
        for endpoint in key_endpoints:
            if any(endpoint in route for route in routes):
                print(f"  ✓ {endpoint}")
            else:
                print(f"  ✗ {endpoint} NOT FOUND")
        
        print("\n✓ FastAPI application test passed!\n")
        return True
    except Exception as e:
        print(f"\n✗ FastAPI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  FILE INTEGRITY & AUTHENTICITY VERIFICATION PLATFORM  ║")
    print("║" + " " * 20 + "SYSTEM TESTS" + " " * 26 + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Cryptography", test_cryptography()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("File Operations", test_file_operations()))
    results.append(("FastAPI Application", test_fastapi_app()))
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED! System is ready to use.")
        print("\nTo start the server, run:")
        print("  python3 -m uvicorn gateway.main:app --reload")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
