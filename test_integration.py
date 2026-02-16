#!/usr/bin/env python3
"""
End-to-End Integration Test - Tests full workflow via API
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def print_status(message, success=True):
    """Print colored status message."""
    symbol = "✓" if success else "✗"
    print(f"{symbol} {message}")

def test_health_check():
    """Test health check endpoint."""
    print("\n" + "="*60)
    print("TESTING HEALTH CHECK")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_status(f"Health check: {data['status']}")
            return True
        else:
            print_status("Health check failed", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False

def test_user_registration():
    """Test user registration."""
    print("\n" + "="*60)
    print("TESTING USER REGISTRATION")
    print("="*60)
    
    username = f"testuser_{int(time.time())}"
    email = f"{username}@example.com"
    password = "TestPassword123"
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password
            }
        )
        
        if response.status_code == 201:
            data = response.json()
            print_status(f"User registered: {data['username']}")
            print(f"  User ID: {data['user_id']}")
            return username, password
        else:
            print_status(f"Registration failed: {response.json()}", False)
            return None, None
    except Exception as e:
        print_status(f"Error: {e}", False)
        return None, None

def test_user_login(username, password):
    """Test user login."""
    print("\n" + "="*60)
    print("TESTING USER LOGIN")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"User logged in: {data['username']}")
            print(f"  Token: {data['access_token'][:32]}...")
            return data['access_token']
        else:
            print_status(f"Login failed: {response.json()}", False)
            return None
    except Exception as e:
        print_status(f"Error: {e}", False)
        return None

def test_file_upload(token, password):
    """Test file upload."""
    print("\n" + "="*60)
    print("TESTING FILE UPLOAD")
    print("="*60)
    
    try:
        # Create test file content
        test_content = b"This is a test file for integrity verification!"
        
        files = {
            'file': ('test_document.txt', test_content, 'text/plain')
        }
        
        data = {
            'password': password,
            'description': 'Integration test file'
        }
        
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(
            f"{API_URL}/files/upload",
            files=files,
            data=data,
            headers=headers
        )
        
        if response.status_code == 201:
            result = response.json()
            print_status(f"File uploaded: {result['filename']}")
            print(f"  File ID: {result['file_id']}")
            print(f"  Size: {result['size']} bytes")
            print(f"  Hash: {result['hash'][:32]}...")
            return result['file_id']
        else:
            print_status(f"Upload failed: {response.json()}", False)
            return None
    except Exception as e:
        print_status(f"Error: {e}", False)
        return None

def test_list_files(token):
    """Test listing files."""
    print("\n" + "="*60)
    print("TESTING FILE LISTING")
    print("="*60)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(
            f"{API_URL}/files",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"Files listed: {data['count']} file(s)")
            for file in data['files'][:3]:  # Show first 3
                print(f"  - {file['filename']} ({file['size']} bytes)")
            return True
        else:
            print_status(f"List failed: {response.json()}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False

def test_file_verification(token, file_id):
    """Test file integrity verification."""
    print("\n" + "="*60)
    print("TESTING FILE VERIFICATION")
    print("="*60)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.post(
            f"{API_URL}/verify/{file_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            verified = result['verified']
            
            if verified:
                print_status("File verification SUCCESSFUL")
                print(f"  Hash Match: {result['hash_match']}")
                print(f"  Signature Valid: {result['signature_valid']}")
                print(f"  Tampered: {result['tampered']}")
            else:
                print_status("File verification FAILED", False)
                print(f"  Details: {result.get('details', {})}")
            
            return verified
        else:
            print_status(f"Verification failed: {response.json()}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False

def test_file_download(token, file_id):
    """Test file download."""
    print("\n" + "="*60)
    print("TESTING FILE DOWNLOAD")
    print("="*60)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(
            f"{API_URL}/files/{file_id}/download",
            headers=headers
        )
        
        if response.status_code == 200:
            content = response.content
            print_status(f"File downloaded: {len(content)} bytes")
            print(f"  Content preview: {content[:50]}...")
            return True
        else:
            print_status(f"Download failed: {response.json()}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False

def test_audit_logs(token):
    """Test audit logs retrieval."""
    print("\n" + "="*60)
    print("TESTING AUDIT LOGS")
    print("="*60)
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        
        response = requests.get(
            f"{API_URL}/audit/logs?limit=5",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print_status(f"Audit logs retrieved: {data['count']} log(s)")
            for log in data['logs'][:3]:  # Show first 3
                print(f"  - {log['action']} at {log['timestamp'][:19]}")
            return True
        else:
            print_status(f"Audit log retrieval failed: {response.json()}", False)
            return False
    except Exception as e:
        print_status(f"Error: {e}", False)
        return False

def main():
    """Run all integration tests."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║       END-TO-END INTEGRATION TEST       ║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Health check
    results.append(("Health Check", test_health_check()))
    
    # User registration
    username, password = test_user_registration()
    results.append(("User Registration", username is not None))
    
    if not username:
        print("\n✗ Cannot continue without user account")
        return 1
    
    # User login
    token = test_user_login(username, password)
    results.append(("User Login", token is not None))
    
    if not token:
        print("\n✗ Cannot continue without authentication")
        return 1
    
    # File upload
    file_id = test_file_upload(token, password)
    results.append(("File Upload", file_id is not None))
    
    if file_id:
        # File listing
        results.append(("File Listing", test_list_files(token)))
        
        # File verification
        results.append(("File Verification", test_file_verification(token, file_id)))
        
        # File download
        results.append(("File Download", test_file_download(token, file_id)))
    
    # Audit logs
    results.append(("Audit Logs", test_audit_logs(token)))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:<30} {status}")
    
    print("-"*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n✓ ALL INTEGRATION TESTS PASSED!")
        print("\nThe File Integrity & Authenticity Verification Platform")
        print("is fully functional and ready for production use!")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
