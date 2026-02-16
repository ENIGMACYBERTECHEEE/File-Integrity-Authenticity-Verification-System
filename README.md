# File Integrity & Authenticity Verification Platform

🔒 A comprehensive microservices platform for secure file integrity verification using SHA-256 hashing, RSA-2048 digital signatures, and AES-256-GCM encryption.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)

## 🌟 Features

- **🔐 File Upload & Encryption**: AES-256-GCM authenticated encryption for secure storage
- **✍️ Digital Signatures**: RSA-2048 signatures for authenticity verification
- **🔍 Hash-based Integrity**: SHA-256 chunk-based hashing for efficient large file processing
- **🔑 JWT Authentication**: Secure token-based user authentication
- **⚡ Rate Limiting**: 100 requests per minute per IP address
- **📊 Audit Logging**: Comprehensive activity tracking and verification history
- **💻 CLI Interface**: User-friendly command-line tool
- **🌐 Web Interface**: Modern React-based dashboard
- **🐳 Docker Support**: Containerized deployment with Docker Compose

## 🏗️ Architecture

Multi-layer microservices architecture:

- **Layer 1**: CLI Client & React Frontend
- **Layer 2**: API Gateway (FastAPI with rate limiting)
- **Layer 3**: Orchestration Layer (Service coordination)
- **Layer 4**: Service Layer (Business logic)
- **Layer 5**: Data Access Layer (Repository pattern)
- **Layer 6**: Persistence Layer (MongoDB)
- **Layer 7**: Infrastructure (Logging, encryption, signatures)

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- Docker Compose
- Git

### 1. Clone Repository

```bash
git clone https://github.com/ENIGMACYBERTECHEEE/File-Integrity-Authenticity-Verification-System.git
cd "File Integrity & Authenticity Verification System"
```

### 2. Start Services

```bash
docker-compose up -d
```

This will start:
- **MongoDB** (port 27017)
- **Backend API** (port 8000)
- **Frontend** (port 3000)

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 4. Login Credentials

**Admin Account:**
```
Username: admin
Password: admin123
```

**Test User Account:**
```
Username: testuser
Password: testpass123
```

### 5. Stop Services

```bash
docker-compose down
```

## 📦 Manual Installation

### Prerequisites

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

### Using the CLI Client

#### Register a New User

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

## ⚙️ Configuration

Key configuration options in `config.py`:

- `MAX_FILE_SIZE_MB`: Maximum file upload size (default: 100MB)
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 100)
- `JWT_EXPIRATION_MINUTES`: Token expiration time (default: 60)
- `RSA_KEY_SIZE`: RSA key size (default: 2048)
- `AES_KEY_SIZE`: AES key size (default: 256 bits)
- `CHUNK_SIZE`: File hashing chunk size (default: 8192 bytes)

Key configuration options in `config.py`:

- `MAX_FILE_SIZE_MB`: Maximum file upload size (default: 100MB)
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 100)
- `JWT_EXPIRATION_MINUTES`: Token expiration time (default: 60)
- `RSA_KEY_SIZE`: RSA key size (default: 2048)

## 📁 Project Structure

```
File-Integrity-Authenticity-Verification-System/
├── 🐳 docker-compose.yml      # Docker orchestration
├── 🐳 Dockerfile              # Backend container definition
├── 📝 README.md               # This file
├── 📝 requirements.txt        # Python dependencies
├── ⚙️ config.py               # Configuration settings
├── 💾 database.py             # MongoDB connection
├── 🌐 gateway/                # API Gateway layer
│   ├── main.py               # FastAPI application
│   ├── auth.py               # JWT authentication
│   ├── rate_limit.py         # Rate limiting middleware
│   └── dependencies.py       # Shared dependencies
├── ⚡ services/               # Service layer (business logic)
│   ├── orchestrator.py       # Service orchestration
│   ├── file_service.py       # File management
│   ├── auth_service.py       # Authentication logic
│   ├── crypto_service.py     # Cryptographic operations
│   ├── verification_service.py # File verification
│   └── audit_service.py      # Audit logging
├── 💾 repositories/           # Data access layer
│   ├── user_repo.py          # User database operations
│   ├── file_repo.py          # File metadata operations
│   ├── verification_repo.py  # Verification records
│   └── key_repo.py           # Cryptographic key storage
├── 🔐 security/               # Cryptographic modules
│   ├── hashing.py            # SHA-256 hashing
│   ├── rsa.py                # RSA signatures
│   ├── aes_storage.py        # AES encryption
│   └── jwt_utils.py          # JWT token handling
├── 💻 cli/                    # Command-line interface
│   └── client.py             # CLI tool
├── 🌐 frontend/               # React web interface
│   ├── index.html            # Main HTML
│   ├── app.jsx               # React application
│   ├── api.js                # API service
│   └── styles.css            # Styling
├── 📦 storage/                # File storage
│   ├── files/                # Encrypted files
│   ├── signatures/           # Digital signatures
│   └── keys/                 # User keys
└── 📊 logs/                   # Application logs
```

## 🔧 Troubleshooting

### Docker Issues

**Container won't start:**
```bash
# Check Docker is running
docker ps

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### MongoDB Connection Issues

**Connection refused:**
```bash
# Check MongoDB is running
docker-compose ps

# Restart MongoDB
docker-compose restart mongodb
```

### Authentication Issues

**"Invalid username or password":**
- Ensure you're using the correct credentials
- Admin: `admin` / `admin123`
- Test user: `testuser` / `testpass123`

**Token expired:**
- Simply log in again to get a new token

### Verification Status Not Updating

**File shows "Pending" after verification:**
1. Click "🔍 Verify" button
2. Click "🔄 Refresh" or reload the page
3. Status should change to "✅ Verified"

### File Upload Issues

**"File too large" error:**
- Maximum file size: 100MB (configurable in `config.py`)

**"Password required" error:**
- You must enter your account password when uploading
- This password is used to sign the file

## 🆕 Recent Updates

### v1.1.0 (Latest)
- ✅ Fixed verification status updates
- ✅ Added proper `verification_status` field tracking
- ✅ Improved verification feedback messages
- ✅ Fixed "Verified Files" counter
- ✅ Enhanced user experience with clear status indicators
- ✅ Updated frontend to show detailed verification results

### v1.0.0
- Initial release with core features
- Docker containerization
- Web and CLI interfaces
- Complete cryptographic implementation

## 🤝 Contributing

This is an academic project for educational purposes. Contributions and suggestions are welcome!

## 📄 License

This project is developed as part of a Bachelor's degree final year project.

## 👨‍💻 Author

**Dipesh Raj Dhakal**
- Email: dipeshrajdhakal@outlook.com
- GitHub: [@ENIGMACYBERTECHEEE](https://github.com/ENIGMACYBERTECHEEE)

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- MongoDB for the reliable database
- React for the frontend framework
- Docker for containerization support

---

**⭐ If you find this project useful, please give it a star on GitHub!**
