# 🔐 File Integrity & Authenticity Verification System

A comprehensive, production-ready platform for secure file storage with cryptographic integrity verification and digital signatures. Built with modern microservices architecture, featuring dual interfaces (Web UI and CLI), real-time monitoring, **role-based access control**, and enterprise-grade security.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248.svg)](https://www.mongodb.com)

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#️-architecture)
- [Technologies](#-technologies)
- [Quick Start](#-quick-start)
- [Using the Web Interface](#-using-the-web-interface)
- [Admin Dashboard](#-admin-dashboard)
- [Using the CLI Client](#-using-the-cli-client)
- [API Endpoints](#-api-endpoints)
- [Configuration](#️-configuration)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Recent Updates](#-recent-updates)

## 🌟 Overview

This system provides a secure platform for storing files with guaranteed integrity and authenticity verification. It combines multiple cryptographic techniques to ensure that uploaded files remain unmodified and can be reliably verified at any time.

The platform features a **unified role-aware dashboard** that automatically adapts to user permissions - regular users get standard file management features, while administrators access a comprehensive 5-tab interface with system-wide controls, user management, and real-time activity monitoring.

## ✨ Key Features

### 🔒 Security Features
- **SHA-256 Hashing**: Cryptographic file integrity verification
- **RSA Digital Signatures**: Authenticity verification (2048-bit keys)
- **AES-256 Encryption**: Secure file storage at rest (GCM mode)
- **JWT Authentication**: Secure user sessions with token-based auth
- **Rate Limiting**: Protection against abuse (100 req/min per IP)
- **Audit Logging**: Complete activity tracking with timeline
- **Role-Based Access Control (RBAC)**: Admin and user permission levels

### 📁 File Management
- **Secure Upload**: Files encrypted with AES-256 before storage
- **Integrity Verification**: Real-time hash comparison
- **Signature Verification**: RSA signature validation
- **Secure Download**: Decryption and verification on-the-fly
- **Batch Verification**: Verify multiple files simultaneously
- **Metadata Storage**: Comprehensive file information
- **System-wide File Browser**: Admins can view/manage all files

### 🎨 User Interface
- **Unified Role-Aware Dashboard**: Single intelligent dashboard for all users
- **Automatic Role Detection**: Dashboard adapts based on user permissions
- **Real-time Updates**: Live verification status via WebSocket
- **File Statistics**: Visual overview with counters and badges
- **Search & Filter**: Easy file discovery
- **Dark Theme**: Eye-friendly interface
- **Status Badges**: Color-coded verification and user status indicators

### 👑 Admin Dashboard (5-Tab Interface)
- **📊 System Statistics**: Total users, files, verifications, storage used
- **👥 User Management**: View all users, activate/deactivate accounts, change roles
- **📁 All Files**: System-wide file browser with delete capability
- **✅ Verification Logs**: Complete verification history with status badges
- **📈 Activity Timeline**: Real-time feed of all system activities

### 💻 Command-Line Interface
- **Full Feature Parity**: All web features available via CLI
- **Scriptable**: Perfect for automation
- **Cross-platform**: Works on Linux, macOS, Windows
- **Interactive**: User-friendly prompts
- **Batch Operations**: Upload/verify multiple files at once

### 📊 Monitoring & Analytics
- **System Health**: Real-time monitoring endpoints
- **Performance Metrics**: Track system performance
- **User Activity Tracking**: Detailed audit logs per user
- **File Statistics**: Comprehensive analytics
- **WebSocket Support**: Real-time updates and notifications
- **Webhook Integration**: External system notifications

### 🔌 API Features
- **RESTful API**: Complete FastAPI backend with OpenAPI docs
- **WebSocket Connections**: Real-time bidirectional communication
- **Webhook Subscriptions**: Register external endpoints for events
- **Batch Operations**: Upload/verify multiple files in one request
- **Admin Endpoints**: 9 dedicated admin management endpoints
- **Rate Limited**: Configurable rate limiting per endpoint

## 🏗️ Architecture

The system follows a clean, layered microservices architecture:

```
┌─────────────────────────────────────────────────────┐
│                   Frontend Layer                     │
│    (React Web UI with Role-Aware Dashboard)         │
│              + CLI Interface                         │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                   API Gateway                        │
│  (FastAPI, JWT Auth, Rate Limiting, WebSocket)      │
│         Role-Based Access Control (RBAC)            │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                  Service Layer                       │
│   Auth | File | Crypto | Verification | Admin       │
│   Audit | Monitoring | Webhook | Orchestrator       │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                Repository Layer                      │
│  User | File | Verification | Key Repositories      │
└─────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              Storage & Message Layer                 │
│  MongoDB | RabbitMQ | Celery Worker | File System   │
└─────────────────────────────────────────────────────┘
```

### Key Components

- **Gateway Layer**: FastAPI-based API with JWT authentication and role-based access control
- **Service Layer**: Business logic separated into focused services:
  - `auth_service.py`: User authentication and authorization
  - `file_service.py`: File upload, download, deletion
  - `crypto_service.py`: Encryption, signatures, hashing
  - `verification_service.py`: File integrity verification
  - `admin_service.py`: Admin operations (NEW in v2.0)
  - `monitoring_service.py`: System health and metrics
  - `webhook_service.py`: Webhook management
  - `audit_service.py`: Activity logging
  - `orchestrator.py`: Service coordination
- **Repository Layer**: Data access abstraction for MongoDB operations
- **Worker Layer**: Celery distributed task queue for async operations
- **Message Broker**: RabbitMQ for task distribution and real-time events

## 🛠️ Technologies

### Backend
- **FastAPI 0.104.1**: Modern, fast web framework with async support
- **Python 3.11**: Latest Python features and performance improvements
- **MongoDB 7.0**: Document database for metadata and audit logs
- **Cryptography**: Industry-standard crypto library
- **PyJWT**: JSON Web Token implementation
- **Celery**: Distributed task queue for async operations
- **RabbitMQ**: Message broker for task distribution
- **bcrypt**: Password hashing with salt

### Frontend
- **React 18**: Component-based UI library with hooks
- **Babel**: JSX transpilation
- **Fetch API**: Modern HTTP client
- **WebSocket**: Real-time bidirectional communication

### DevOps
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container orchestration (5 services)
- **Nginx**: Web server and reverse proxy
- **Health Checks**: Container monitoring and auto-recovery

### Security Libraries
- **hashlib**: SHA-256 hashing
- **cryptography**: RSA-2048 and AES-256-GCM operations
- **PyJWT**: Secure token handling with role claims
- **bcrypt**: Password hashing with salt

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** (macOS/Windows) or **Docker Engine** (Linux)
- **Docker Compose** v2.0+
- **Git**

### 1. Clone Repository

```bash
git clone <repository-url>
cd "File Integrity & Authenticity Verification System"
```

### 2. Start All Services

```bash
docker-compose up -d
```

This starts 5 containers:
- **MongoDB** (port 27017) - Database
- **RabbitMQ** (port 5672) - Message broker
- **Backend API** (port 8000) - FastAPI server
- **Celery Worker** - Async task processor
- **Frontend** (port 3000) - React web UI

### 3. Verify Services

```bash
docker-compose ps
```

All services should show "Up" status (some may show "health: starting" initially).

### 4. Access the Application

- **Web Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/monitoring/health

### 5. Login Credentials

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

### 6. Stop Services

```bash
docker-compose down
```

To remove volumes (database data):
```bash
docker-compose down -v
```

## 🌐 Using the Web Interface

The web interface provides a unified, role-aware dashboard that automatically adapts to user permissions.

### Access the Dashboard

1. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

2. **Login** with credentials (see above)

**Important:** All users access the same URL - the dashboard automatically detects your role and shows appropriate features.

### Regular User Dashboard

**📊 Dashboard Overview:**
- Total files uploaded
- Total verifications performed
- Verified files count
- Failed verifications count

**📁 File Management:**
- **Upload** new files with descriptions
- **View** your uploaded files in a table
- **Download** files securely with automatic decryption
- **Delete** unwanted files
- **Verify** file integrity with one click
- **Batch verification** (verify all files)

**🔍 File Verification:**
1. Click the "🔍 Verify" button next to any file
2. Verification happens in real-time
3. See immediate status update with colored badges
4. View detailed verification results (hash match, signature valid)

**File Information Displayed:**
- Filename
- Description
- Upload date/time
- File size
- Verification status with badges:
  - 🟢 **Verified** (green badge)
  - 🔴 **Failed** (red badge)
  - 🟡 **Pending** (yellow badge)
- SHA-256 hash
- RSA signature

### Creating a New User

Register directly from the web interface:
1. Go to `http://localhost:3000`
2. Click "Need an account? Register"
3. Fill in username, email, and password
4. Login with your new credentials
5. Default role: Regular user

## 🔑 Admin Dashboard

Administrators get a comprehensive **5-tab interface** with system-wide controls.

### Admin Features

When you log in as an admin, the dashboard shows an **ADMIN** badge in the header and provides 5 tabs:

#### Tab 1: 📁 My Files
- Same features as regular users
- Upload, download, verify, delete your own files
- File statistics dashboard

#### Tab 2: 👥 All Users
- **View all registered users** in a table
- **User information:**
  - Username
  - Email
  - Role (Admin/User badge)
  - Account status (Active/Inactive badge)
  - Registration date
- **User management actions:**
  - **Activate/Deactivate** user accounts
  - **Change user roles** (promote to admin or demote to user)
- **Real-time updates** after each action

#### Tab 3: 📂 All Files
- **System-wide file browser** showing all files from all users
- **File details:**
  - Filename
  - Owner (username)
  - Upload date
  - File size
  - Verification status
  - SHA-256 hash
- **Admin actions:**
  - **Download any file** (with automatic decryption)
  - **Delete any file permanently** (with confirmation)
- **Complete control** over system storage

#### Tab 4: ✅ Verifications
- **Complete verification history** for all files
- **Verification log details:**
  - File ID
  - Verification date/time
  - Result (Success/Failed) with colored badges
  - Hash match status
  - Signature validity
  - Performed by user
- **Filter and search** verification records
- **Audit trail** for all verification attempts

#### Tab 5: 📈 Activity Timeline
- **Real-time activity feed** showing all system events
- **Activity types tracked:**
  - User registrations
  - File uploads
  - File verifications
  - File downloads
  - File deletions
  - User role changes
- **Activity details:**
  - Event type
  - Timestamp
  - User who performed action
  - Details and metadata
- **Chronological order** (newest first)
- **Comprehensive audit log** for security and compliance

### System Statistics

Admins see enhanced statistics at the top:
- 👥 **Total Users** registered
- 📁 **Total Files** in system
- ✅ **Total Verifications** performed
- 💾 **Storage Used** (in MB)

### Creating Admin Users

**Method 1: Using the admin dashboard**
1. Log in as an existing admin
2. Go to "All Users" tab
3. Find the user you want to promote
4. Click "👑 Make Admin"
5. User immediately gains admin privileges

**Method 2: Using the setup script**
```bash
# Create a new admin user from command line
python create_admin.py
```

**Method 3: Promote existing user via script**
```bash
# Promote testuser to admin
python setup_users.py
```

## 💻 Using the CLI Client

The CLI provides full feature parity with the web interface.

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

## 🔌 API Endpoints

The system provides a comprehensive RESTful API with role-based access control.

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Register new user | No |
| POST | `/api/v1/auth/login` | User login (returns JWT) | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |

### File Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/files/upload` | Upload a new file | Yes |
| GET | `/api/v1/files` | List user's files | Yes |
| GET | `/api/v1/files/{file_id}` | Get file metadata | Yes |
| GET | `/api/v1/files/{file_id}/download` | Download file | Yes |
| DELETE | `/api/v1/files/{file_id}` | Delete file | Yes |

### Verification Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/verify/{file_id}` | Verify file integrity | Yes |
| GET | `/api/v1/verify/{file_id}/history` | Get verification history | Yes |
| POST | `/api/v1/verify/batch` | Verify multiple files | Yes |

### Admin Endpoints (Admin Role Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/stats` | System statistics (users, files, verifications, storage) |
| GET | `/api/v1/admin/users` | List all users with details |
| GET | `/api/v1/admin/files` | List all files system-wide |
| GET | `/api/v1/admin/verifications` | Get all verification logs |
| PATCH | `/api/v1/admin/users/{user_id}/status` | Activate/deactivate user |
| PATCH | `/api/v1/admin/users/{user_id}/role` | Change user role (admin/user) |
| DELETE | `/api/v1/admin/files/{file_id}` | Delete any file permanently |
| GET | `/api/v1/admin/users/{user_id}/activity` | Get user activity log |
| GET | `/api/v1/admin/activity-timeline` | Get system-wide activity timeline |

### Monitoring Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/monitoring/health` | System health check | No |
| GET | `/api/v1/monitoring/metrics` | Performance metrics | Yes (Admin) |

### Webhook Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/webhooks/subscribe` | Subscribe to events | Yes |
| GET | `/api/v1/webhooks/subscriptions` | List your webhooks | Yes |
| DELETE | `/api/v1/webhooks/{webhook_id}` | Delete webhook | Yes |

### WebSocket Endpoints

| Endpoint | Description | Auth Required |
|----------|-------------|---------------|
| `/ws` | WebSocket connection for real-time updates | Yes (token in query) |

### API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Both provide interactive testing interfaces for all endpoints.

## ⚙️ Configuration

Key configuration options in `config.py`:

### Security Settings
- `MAX_FILE_SIZE_MB`: Maximum file upload size (default: 100MB)
- `JWT_SECRET_KEY`: Secret key for JWT tokens (change in production!)
- `JWT_EXPIRATION_MINUTES`: Token expiration time (default: 60)
- `RSA_KEY_SIZE`: RSA key size (default: 2048)
- `AES_KEY_SIZE`: AES key size (default: 256 bits)

### Rate Limiting
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 100)
- Rate limiting applies per IP address

### Cryptography
- `CHUNK_SIZE`: File hashing chunk size (default: 8192 bytes)
- `HASH_ALGORITHM`: SHA-256 (configurable)

### Database
- `MONGODB_URL`: MongoDB connection string
- `MONGODB_DB_NAME`: Database name

### File Storage
- `STORAGE_PATH`: Base path for file storage
- Files are stored encrypted in `storage/files/`
- Signatures in `storage/signatures/`
- Keys in `storage/keys/`

## 📁 Project Structure

```
File-Integrity-Authenticity-Verification-System/
├── 🐳 docker-compose.yml      # Docker orchestration (5 services)
├── 🐳 Dockerfile              # Backend container definition
├── 📝 README.md               # This file
├── 📝 requirements.txt        # Python dependencies
├── ⚙️ config.py               # Configuration settings
├── 💾 database.py             # MongoDB connection
├── 🔧 create_admin.py         # Admin user creation script
├── 🔧 setup_users.py          # User management script
├── 🌐 gateway/                # API Gateway layer
│   ├── main.py               # FastAPI application (30+ endpoints)
│   ├── auth.py               # JWT authentication
│   ├── rate_limit.py         # Rate limiting middleware
│   ├── dependencies.py       # Shared dependencies (admin checker)
│   └── websocket_manager.py  # WebSocket connection manager
├── ⚡ services/               # Service layer (business logic)
│   ├── orchestrator.py       # Service orchestration
│   ├── file_service.py       # File management
│   ├── auth_service.py       # Authentication logic
│   ├── crypto_service.py     # Cryptographic operations
│   ├── verification_service.py # File verification
│   ├── audit_service.py      # Audit logging
│   ├── admin_service.py      # Admin operations (NEW)
│   ├── monitoring_service.py # System monitoring
│   └── webhook_service.py    # Webhook management
├── 💾 repositories/           # Data access layer
│   ├── user_repo.py          # User database operations
│   ├── file_repo.py          # File metadata operations
│   ├── verification_repo.py  # Verification records
│   └── key_repo.py           # Cryptographic key storage
├── 🔐 security/               # Cryptographic modules
│   ├── hashing.py            # SHA-256 hashing
│   ├── rsa.py                # RSA signatures
│   ├── aes_storage.py        # AES-256-GCM encryption
│   └── jwt_utils.py          # JWT token handling
├── 💻 cli/                    # Command-line interface
│   ├── client.py             # CLI tool
│   └── file_integrity_cli.py # Alternative CLI
├── 🌐 frontend/               # React web interface
│   ├── index.html            # Landing page
│   ├── login.html            # Login page
│   ├── dashboard.html        # Dashboard page
│   ├── app.jsx               # React app with role-aware dashboard
│   ├── api.js                # API service client
│   └── styles.css            # Styling with badges and tables
├── 📦 storage/                # File storage
│   ├── files/                # Encrypted files (AES-256-GCM)
│   ├── signatures/           # Digital signatures (RSA-2048)
│   └── keys/                 # User keys
├── 👷 workers/                # Celery worker tasks
│   ├── celery_app.py         # Celery configuration
│   └── tasks.py              # Async tasks
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
docker-compose logs celery_worker
docker-compose logs rabbitmq

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**"Port already in use" error:**
```bash
# Check what's using the ports
# macOS/Linux:
lsof -i :3000
lsof -i :8000
lsof -i :27017

# Windows:
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# Kill the process or change ports in docker-compose.yml
```

### MongoDB Connection Issues

**Connection refused:**
```bash
# Check MongoDB is running
docker-compose ps

# Restart MongoDB
docker-compose restart mongodb

# Check MongoDB logs
docker-compose logs mongodb
```

### Authentication Issues

**"Invalid username or password":**
- Ensure you're using the correct credentials
- Admin: `admin` / `admin123`
- Test user: `testuser` / `testpass123`

**Token expired:**
- Simply log in again to get a new token
- Default expiration: 60 minutes (configurable in `config.py`)

**Admin features not showing:**
- Verify you're logged in with an admin account
- Check if the "ADMIN" badge appears in the dashboard header
- Admin role is stored in JWT token - may need to log out and back in
- Use admin dashboard to promote users to admin role

### Verification Status Not Updating

**File shows "Pending" after verification:**
1. Click "🔍 Verify" button
2. Click "🔄 Refresh" or reload the page
3. Status should change to "✅ Verified"
4. Check backend logs for verification errors

### File Upload Issues

**"File too large" error:**
- Maximum file size: 100MB (configurable in `config.py`)
- Increase `MAX_FILE_SIZE_MB` in config if needed

**"Password required" error:**
- You must enter your account password when uploading
- This password is used to sign the file with your RSA key

### Container Health Issues

**Container shows "unhealthy" status:**
```bash
# Check container logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>

# Full restart
docker-compose restart
```

## 🆕 Recent Updates

### v2.0.0 (Latest) - Unified Role-Aware Dashboard
- ✅ **Unified Dashboard**: Single intelligent dashboard for all users
- ✅ **Automatic Role Detection**: Dashboard adapts based on user permissions
- ✅ **5-Tab Admin Interface**: Comprehensive admin controls
  - My Files: Personal file management
  - All Users: System-wide user management
  - All Files: Complete file browser
  - Verifications: Audit trail of all verifications
  - Activity: Real-time system activity feed
- ✅ **User Management**: Activate/deactivate accounts, change roles
- ✅ **System-wide File Browser**: Admins can view and manage all files
- ✅ **Verification Logs**: Complete audit trail for all verifications
- ✅ **Activity Timeline**: Real-time system activity feed
- ✅ **Enhanced UI**: Status badges (verified, failed, pending, active, inactive)
- ✅ **Role-Based Access Control**: Admin endpoints with permission checking
- ✅ **System Statistics**: Total users, files, verifications, storage metrics
- ✅ **Admin Service**: New service layer for administrative operations

### v1.5.0 - Advanced Features
- ✅ **WebSocket Support**: Real-time updates and notifications
- ✅ **Webhook Integration**: External system notifications
- ✅ **Batch Operations**: Upload/verify multiple files simultaneously
- ✅ **Monitoring Endpoints**: System health and performance metrics
- ✅ **Celery Workers**: Distributed task processing with RabbitMQ
- ✅ **Audit Logging**: Comprehensive activity tracking
- ✅ **Enhanced Security**: Improved JWT handling and role claims

### v1.1.0
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
- The open-source community for cryptographic libraries

---

**⭐ If you find this project useful, please give it a star on GitHub!**
