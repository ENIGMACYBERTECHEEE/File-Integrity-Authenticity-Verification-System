#!/usr/bin/env python3
"""
File Integrity CLI Client - Command Line Interface for file operations.
"""
import click
import requests
import json
import os
from pathlib import Path
from typing import Optional
import getpass

# API Base URL
API_BASE = os.getenv("API_URL", "http://localhost:8000/api/v1")
TOKEN_FILE = Path.home() / ".file_integrity_token"


class APIClient:
    """API Client for CLI operations."""
    
    def __init__(self):
        self.token = self._load_token()
        
    def _load_token(self) -> Optional[str]:
        """Load saved token from file."""
        if TOKEN_FILE.exists():
            return TOKEN_FILE.read_text().strip()
        return None
    
    def _save_token(self, token: str):
        """Save token to file."""
        TOKEN_FILE.write_text(token)
        TOKEN_FILE.chmod(0o600)
    
    def _get_headers(self):
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """Login and save token."""
        response = requests.post(
            f"{API_BASE}/auth/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self._save_token(self.token)
            return True
        return False
    
    def upload_file(self, file_path: str, password: str, description: Optional[str] = None):
        """Upload file for verification."""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'password': password}
            if description:
                data['description'] = description
            
            response = requests.post(
                f"{API_BASE}/files/upload",
                headers={"Authorization": f"Bearer {self.token}"},
                files=files,
                data=data
            )
            return response.json()
    
    def list_files(self):
        """List all files."""
        response = requests.get(
            f"{API_BASE}/files",
            headers=self._get_headers()
        )
        return response.json()
    
    def verify_file(self, file_id: str):
        """Verify a file."""
        response = requests.post(
            f"{API_BASE}/verify/{file_id}",
            headers=self._get_headers()
        )
        return response.json()
    
    def download_file(self, file_id: str, output_path: str):
        """Download a file."""
        response = requests.get(
            f"{API_BASE}/files/{file_id}/download",
            headers=self._get_headers()
        )
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False


client = APIClient()


@click.group()
def cli():
    """File Integrity & Authenticity Verification CLI."""
    pass


@cli.command()
@click.option('--username', prompt=True, help='Your username')
@click.option('--password', prompt=True, hide_input=True, help='Your password')
def login(username, password):
    """Login to the system."""
    if client.login(username, password):
        click.echo(click.style("✓ Login successful!", fg='green'))
    else:
        click.echo(click.style("✗ Login failed!", fg='red'))


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--password', prompt=True, hide_input=True, help='Your account password')
@click.option('--description', help='File description')
def upload(file_path, password, description):
    """Upload a file for verification."""
    if not client.token:
        click.echo(click.style("✗ Please login first!", fg='red'))
        return
    
    try:
        click.echo(f"Uploading {file_path}...")
        result = client.upload_file(file_path, password, description)
        click.echo(click.style(f"✓ File uploaded successfully!", fg='green'))
        click.echo(f"File ID: {result.get('file_id')}")
        click.echo(f"Hash: {result.get('file_hash')}")
    except Exception as e:
        click.echo(click.style(f"✗ Upload failed: {str(e)}", fg='red'))


@cli.command()
def list():
    """List all your files."""
    if not client.token:
        click.echo(click.style("✗ Please login first!", fg='red'))
        return
    
    try:
        result = client.list_files()
        files = result.get('files', [])
        
        if not files:
            click.echo("No files found.")
            return
        
        click.echo(f"\n{'Filename':<30} {'Status':<15} {'Hash':<20}")
        click.echo("-" * 70)
        
        for file in files:
            status = file.get('verification_status', 'unknown')
            status_color = 'green' if status == 'verified' else 'yellow' if status == 'pending' else 'red'
            
            click.echo(
                f"{file.get('filename', ''):<30} "
                f"{click.style(status, fg=status_color):<15} "
                f"{file.get('file_hash', '')[:16]:<20}..."
            )
    except Exception as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))


@cli.command()
@click.argument('file_id')
def verify(file_id):
    """Verify a file's integrity."""
    if not client.token:
        click.echo(click.style("✗ Please login first!", fg='red'))
        return
    
    try:
        click.echo(f"Verifying file {file_id}...")
        result = client.verify_file(file_id)
        
        status = result.get('verification_status')
        if status == 'verified':
            click.echo(click.style("✓ File is VERIFIED - Integrity intact!", fg='green'))
        elif status == 'tampered':
            click.echo(click.style("✗ File is TAMPERED - Integrity compromised!", fg='red'))
        else:
            click.echo(click.style(f"? File status: {status}", fg='yellow'))
            
        click.echo(f"Hash: {result.get('file_hash')}")
    except Exception as e:
        click.echo(click.style(f"✗ Verification failed: {str(e)}", fg='red'))


@cli.command()
@click.argument('file_id')
@click.argument('output_path', type=click.Path())
def download(file_id, output_path):
    """Download a file."""
    if not client.token:
        click.echo(click.style("✗ Please login first!", fg='red'))
        return
    
    try:
        click.echo(f"Downloading file {file_id}...")
        if client.download_file(file_id, output_path):
            click.echo(click.style(f"✓ File downloaded to {output_path}", fg='green'))
        else:
            click.echo(click.style("✗ Download failed!", fg='red'))
    except Exception as e:
        click.echo(click.style(f"✗ Error: {str(e)}", fg='red'))


@cli.command()
def logout():
    """Logout from the system."""
    if TOKEN_FILE.exists():
        TOKEN_FILE.unlink()
    click.echo(click.style("✓ Logged out successfully!", fg='green'))


if __name__ == '__main__':
    cli()
