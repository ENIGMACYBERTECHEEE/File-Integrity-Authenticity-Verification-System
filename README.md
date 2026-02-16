# File Integrity & Authenticity Verification Platform

A multi-layer microservices platform for secure file integrity verification using SHA-256 hashing, RSA-2048 digital signatures, and AES-256-GCM encryption.

## Features

- **File Upload & Encryption**: Files are encrypted with AES-256-GCM before storage
- **Digital Signatures**: RSA-2048 signatures for authenticity verification
- **Hash-based Integrity**: SHA-256 chunk-based hashing for large files
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: 100 requests per minute per IP
- **Audit Logging**: Comprehensive activity tracking
- **CLI Interface**: User-friendly command-line tool

## Architecture

- **Layer 1**: CLI Client
- **Layer 2**: API Gateway (FastAPI)
- **Layer 3**: Application Layer (Orchestrator)
- **Layer 4**: Service Layer (Business Logic)
- **Layer 5**: Data Access Layer (Repositories)
- **Layer 6**: Persistence Layer (MongoDB)
- **Layer 7**: Infrastructure (Logging, Background Tasks)

## Prerequisites

- Python 3.8 or higher
- MongoDB 4.0 or higher

## Setup

### 1. Install MongoDB

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Ubuntu/Debian:**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 2. Clone and Setup Project

```bash
cd "File Integrity & Authenticity Verification System"
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

Edit `.env` and update the following (optional, defaults will work):
```
MONGO_URI=mongodb://localhost:27017/
DATABASE_NAME=file_integrity_db
JWT_SECRET_KEY=your-secret-key-change-in-production
MASTER_KEY=your-master-encryption-key-32-bytes
```

## Running the Server

Start the FastAPI server:

```bash
uvicorn gateway.main:app --reload
```

The server will start at `http://localhost:8000`

API Documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Using the CLI Client

### Register a New User

```bash
python cli/client.py register
```

### Login

```bash
python cli/client.py login
```

### Upload a File

```bash
python cli/client.py upload /path/to/file.txt --description "Important document"
```

### List Files

```bash
python cli/client.py list
```

### Verify File Integrity

```bash
python cli/client.py verify <file_id>
```

### Download a File

```bash
python cli/client.py download <file_id> --output /path/to/save/file.txt
```

### Delete a File

```bash
python cli/client.py delete <file_id>
```

### Check Authentication Status

```bash
python cli/client.py status
```

## API Endpoints

### Public Endpoints (No Authentication)

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Protected Endpoints (Require JWT Token)

- `POST /api/v1/files/upload` - Upload a file
- `GET /api/v1/files` - List user's files
- `GET /api/v1/files/{file_id}` - Get file metadata
- `GET /api/v1/files/{file_id}/download` - Download file
- `DELETE /api/v1/files/{file_id}` - Delete file
- `POST /api/v1/verify/{file_id}` - Verify file integrity
- `POST /api/v1/verify/batch` - Verify multiple files
- `GET /api/v1/audit/logs` - Get audit logs
- `GET /health` - Health check

## Security Features

### Cryptographic Operations

- **SHA-256**: Chunk-based hashing (8192 bytes) for efficient processing of large files
- **RSA-2048**: Digital signatures for authenticity verification
- **AES-256-GCM**: Authenticated encryption for file storage
- **PBKDF2**: Key derivation (100,000 iterations)

### File Verification Workflow

1. Validate file exists and check permissions
2. Decrypt file from storage
3. Recompute SHA-256 hash
4. Compare computed hash with stored hash
5. Verify RSA signature using public key
6. Determine verification status (both hash and signature must match)
7. Save verification record
8. Update file metadata
9. Log audit event

## Configuration

Key configuration options in `config.py`:

- `MAX_FILE_SIZE_MB`: Maximum file upload size (default: 100MB)
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 100)
- `JWT_EXPIRATION_MINUTES`: Token expiration time (default: 60)
- `RSA_KEY_SIZE`: RSA key size (default: 2048)

## Project Structure

```
file-integrity-platform/
├── gateway/              # API Gateway layer
│   ├── main.py          # FastAPI application
│   ├── auth.py          # JWT authentication
│   ├── rate_limit.py    # Rate limiting
│   └── dependencies.py  # Shared dependencies
├── services/            # Service layer
│   ├── orchestrator.py
│   ├── file_service.py
│   ├── auth_service.py
│   ├── crypto_service.py
│   ├── verification_service.py
│   └── audit_service.py
├── repositories/        # Data access layer
│   ├── user_repo.py
│   ├── file_repo.py
│   ├── verification_repo.py
│   └── key_repo.py
├── security/           # Cryptographic operations
│   ├── hashing.py
│   ├── rsa.py
│   ├── aes_storage.py
│   └── jwt_utils.py
├── cli/                # CLI client
│   └── client.py
├── storage/            # File storage
│   ├── files/
│   ├── signatures/
│   └── keys/
├── logs/               # Application logs
├── config.py           # Configuration
├── database.py         # MongoDB connection
└── requirements.txt    # Dependencies
```

## Troubleshooting

### MongoDB Connection Issues

Ensure MongoDB is running:
```bash
# macOS
brew services list

# Linux
sudo systemctl status mongodb
```

### Permission Errors

Ensure storage directories have correct permissions:
```bash
chmod 755 storage/
chmod 755 logs/
```

### Token Issues

If authentication fails, delete the token file:
```bash
rm ~/.file_integrity_token
```

Then login again.

## License

This is a bachelor's final year project for educational purposes.
