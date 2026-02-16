#!/usr/bin/env python3
"""
CLI Client for File Integrity & Authenticity Verification Platform.
"""
import sys
import argparse
import requests
from pathlib import Path
from typing import Optional
import json
from getpass import getpass
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TOKEN_FILE = Path.home() / ".file_integrity_token"


class APIClient:
    """Client for interacting with the API Gateway."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize API client."""
        self.base_url = base_url
        self.token = self._load_token()
    
    def _load_token(self) -> Optional[str]:
        """Load stored JWT token."""
        if TOKEN_FILE.exists():
            try:
                return TOKEN_FILE.read_text().strip()
            except Exception:
                return None
        return None
    
    def _save_token(self, token: str) -> None:
        """Save JWT token to file."""
        try:
            TOKEN_FILE.write_text(token)
            TOKEN_FILE.chmod(0o600)
        except Exception as e:
            print(f"{Fore.RED}Error saving token: {e}")
    
    def _delete_token(self) -> None:
        """Delete stored token."""
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
    
    def _get_headers(self) -> dict:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, username: str, email: str, password: str) -> bool:
        """Register a new user."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"{Fore.GREEN}✓ Registration successful!")
                print(f"{Fore.CYAN}User ID: {data['user_id']}")
                print(f"{Fore.CYAN}Username: {data['username']}")
                return True
            else:
                error = response.json().get("detail", "Registration failed")
                print(f"{Fore.RED}✗ {error}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """Login and save token."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                self._save_token(self.token)
                print(f"{Fore.GREEN}✓ Login successful!")
                print(f"{Fore.CYAN}Welcome, {data['username']}!")
                return True
            else:
                error = response.json().get("detail", "Login failed")
                print(f"{Fore.RED}✗ {error}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False
    
    def upload_file(self, filepath: str, password: str, description: Optional[str] = None) -> bool:
        """Upload a file."""
        if not self.token:
            print(f"{Fore.RED}✗ Not authenticated. Please login first.")
            return False
        
        file_path = Path(filepath)
        if not file_path.exists():
            print(f"{Fore.RED}✗ File not found: {filepath}")
            return False
        
        try:
            file_size = file_path.stat().st_size
            
            with open(file_path, "rb") as f:
                files = {"file": (file_path.name, f, "application/octet-stream")}
                data = {"password": password}
                if description:
                    data["description"] = description
                
                headers = {"Authorization": f"Bearer {self.token}"}
                
                print(f"{Fore.CYAN}Uploading {file_path.name}...")
                
                response = requests.post(
                    f"{self.base_url}/files/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            if response.status_code == 201:
                result = response.json()
                print(f"{Fore.GREEN}✓ Upload successful!")
                print(f"{Fore.CYAN}File ID: {result['file_id']}")
                print(f"{Fore.CYAN}Filename: {result['filename']}")
                print(f"{Fore.CYAN}Size: {result['size']} bytes")
                print(f"{Fore.CYAN}Hash: {result['hash']}")
                return True
            else:
                error = response.json().get("detail", "Upload failed")
                print(f"{Fore.RED}✗ {error}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False
    
    def list_files(self) -> bool:
        """List user's files."""
        if not self.token:
            print(f"{Fore.RED}✗ Not authenticated. Please login first.")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/files",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                files = data.get("files", [])
                
                if not files:
                    print(f"{Fore.YELLOW}No files found.")
                    return True
                
                print(f"\n{Fore.CYAN}{'File ID':<38} {'Filename':<30} {'Size':<12} {'Verifications'}")
                print(f"{Fore.CYAN}{'-' * 100}")
                
                for file in files:
                    file_id = file.get("file_id", "")
                    filename = file.get("filename", "")[:28]
                    size = file.get("size", 0)
                    verifications = file.get("verification_count", 0)
                    
                    print(f"{file_id:<38} {filename:<30} {size:<12} {verifications}")
                
                print(f"\n{Fore.GREEN}Total files: {len(files)}")
                return True
            else:
                error = response.json().get("detail", "Failed to list files")
                print(f"{Fore.RED}✗ {error}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False
    
    def download_file(self, file_id: str, output_path: Optional[str] = None) -> bool:
        """Download a file."""
        if not self.token:
            print(f"{Fore.RED}✗ Not authenticated. Please login first.")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(
                f"{self.base_url}/files/{file_id}/download",
                headers=headers,
                stream=True
            )
            
            if response.status_code == 200:
                # Get filename from Content-Disposition header
                content_disposition = response.headers.get("Content-Disposition", "")
                if 'filename="' in content_disposition:
                    filename = content_disposition.split('filename="')[1].rstrip('"')
                else:
                    filename = f"downloaded_{file_id}"
                
                output_file = Path(output_path) if output_path else Path(filename)
                
                total_size = int(response.headers.get('content-length', 0))
                
                with open(output_file, "wb") as f:
                    if total_size > 0:
                        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                pbar.update(len(chunk))
                    else:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                
                print(f"{Fore.GREEN}✓ File downloaded: {output_file}")
                return True
            else:
                error = response.json().get("detail", "Download failed")
                print(f"{Fore.RED}✗ {error}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False
    
    def verify_file(self, file_id: str) -> bool:
        """Verify file integrity."""
        if not self.token:
            print(f"{Fore.RED}✗ Not authenticated. Please login first.")
            return False
        
        try:
            print(f"{Fore.CYAN}Verifying file {file_id}...")
            
            response = requests.post(
                f"{self.base_url}/verify/{file_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                verified = result.get("verified", False)
                
                if verified:
                    print(f"{Fore.GREEN}✓ VERIFICATION SUCCESSFUL")
                    print(f"{Fore.GREEN}  File integrity: INTACT")
                    print(f"{Fore.GREEN}  Digital signature: VALID")
                else:
                    print(f"{Fore.RED}✗ VERIFICATION FAILED")
                    if not result.get("hash_match"):
                        print(f"{Fore.RED}  File integrity: COMPROMISED (hash mismatch)")
                    if not result.get("signature_valid"):
                        print(f"{Fore.RED}  Digital signature: INVALID")
                
                print(f"\n{Fore.CYAN}Details:")
                print(f"{Fore.CYAN}  Filename: {result.get('filename')}")
                print(f"{Fore.CYAN}  Timestamp: {result.get('timestamp')}")
                print(f"{Fore.CYAN}  Hash Match: {result.get('hash_match')}")
                print(f"{Fore.CYAN}  Signature Valid: {result.get('signature_valid')}")
                
                return verified
            else:
                error = response.json().get("detail", "Verification failed")
                print(f"{Fore.RED}✗ {error}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        if not self.token:
            print(f"{Fore.RED}✗ Not authenticated. Please login first.")
            return False
        
        try:
            response = requests.delete(
                f"{self.base_url}/files/{file_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}✓ File deleted successfully")
                return True
            else:
                error = response.json().get("detail", "Delete failed")
                print(f"{Fore.RED}✗ {error}")
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False
    
    def status(self) -> bool:
        """Check authentication status."""
        if not self.token:
            print(f"{Fore.YELLOW}Not authenticated")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/files",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}✓ Authenticated")
                return True
            else:
                print(f"{Fore.RED}✗ Token expired or invalid")
                self._delete_token()
                return False
        except Exception as e:
            print(f"{Fore.RED}✗ Error: {e}")
            return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="File Integrity & Authenticity Verification CLI"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new user")
    
    # Login command
    login_parser = subparsers.add_parser("login", help="Login to the platform")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("filepath", help="Path to the file to upload")
    upload_parser.add_argument("--description", help="File description")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List your files")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download a file")
    download_parser.add_argument("file_id", help="File ID to download")
    download_parser.add_argument("--output", help="Output file path")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify file integrity")
    verify_parser.add_argument("file_id", help="File ID to verify")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a file")
    delete_parser.add_argument("file_id", help="File ID to delete")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check authentication status")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = APIClient()
    
    if args.command == "register":
        print(f"{Fore.CYAN}=== User Registration ===")
        username = input("Username: ")
        email = input("Email: ")
        password = getpass("Password: ")
        confirm_password = getpass("Confirm Password: ")
        
        if password != confirm_password:
            print(f"{Fore.RED}✗ Passwords do not match")
            sys.exit(1)
        
        client.register(username, email, password)
    
    elif args.command == "login":
        print(f"{Fore.CYAN}=== Login ===")
        username = input("Username: ")
        password = getpass("Password: ")
        
        client.login(username, password)
    
    elif args.command == "upload":
        password = getpass("Enter your password for signing: ")
        client.upload_file(args.filepath, password, args.description)
    
    elif args.command == "list":
        client.list_files()
    
    elif args.command == "download":
        client.download_file(args.file_id, args.output)
    
    elif args.command == "verify":
        client.verify_file(args.file_id)
    
    elif args.command == "delete":
        confirm = input(f"Are you sure you want to delete file {args.file_id}? (yes/no): ")
        if confirm.lower() == "yes":
            client.delete_file(args.file_id)
        else:
            print(f"{Fore.YELLOW}Cancelled")
    
    elif args.command == "status":
        client.status()


if __name__ == "__main__":
    main()
