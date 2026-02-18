# 🔐 File Integrity & Authenticity Verification System

A comprehensive enterprise-grade platform for secure file integrity verification using cryptographic signatures and distributed architecture.

## 🏗️ Architecture Overview

### Multi-Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Web    │  │   CLI    │  │  Mobile  │  │  IDE/API │   │
│  │Dashboard │  │ (Click)  │  │   App    │  │  Client  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    GATEWAY LAYER                             │
│  FastAPI Gateway (JWT Auth, Rate Limiting, WebSocket)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 INFRASTRUCTURE LAYER                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ RabbitMQ │  │  Celery  │  │   MCP    │                 │
│  │  Broker  │  │  Worker  │  │  Proxy   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    SERVICES LAYER                            │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│  │    File    │ │   User &   │ │  Webhook   │             │
│  │ Management │ │    Auth    │ │  Manager   │             │
│  └────────────┘ └────────────┘ └────────────┘             │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│  │Cryptographic│ │Verification│ │ Monitoring │             │
│  │  Service   │ │  Service   │ │   Service  │             │
│  └────────────┘ └────────────┘ └────────────┘             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  DATA ACCESS LAYER                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │   File   │  │   User   │  │Verification│                │
│  │Repository│  │Repository│  │ Repository │                │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 PERSISTENCE LAYER                            │
│                  MongoDB 7.0                                 │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### Core Functionality
- ✅ **SHA-256 Hashing** - Cryptographic file integrity verification
- ✅ **RSA-2048 Signatures** - Digital signature generation and verification
- ✅ **AES-256-GCM Encryption** - Secure key storage
- ✅ **JWT Authentication** - Secure user authentication
- ✅ **Role-Based Access Control** - Admin and user roles

### Advanced Features
- 🚀 **Async Task Processing** - Background verification with Celery
- 📡 **WebSocket Support** - Real-time updates and notifications
- 🔔 **Webhook System** - Event-driven notifications
- 📊 **Monitoring & Metrics** - System health and performance tracking
- 🖥️ **CLI Client** - Command-line file management
- 🌐 **REST API** - Full-featured API with OpenAPI docs
- 📝 **Audit Logging** - Complete activity trail

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for CLI)
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd "File Integrity & Authenticity Verification System"

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React web dashboard |
| API Docs | http://localhost:8000/docs | Swagger UI documentation |
| RabbitMQ Management | http://localhost:15672 | Message queue dashboard |
| Health Check | http://localhost:8000/health | System health status |

### Default Credentials

- **Admin**: `admin` / `admin123`
- **RabbitMQ**: `admin` / `admin123`

## 📱 Usage

### Web Dashboard

1. Navigate to http://localhost:3000
2. Login with your credentials
3. Upload files for verification
4. Monitor file status and verification results
5. Download verified files

### CLI Client

```bash
# Make CLI executable
chmod +x cli/file_integrity_cli.py

# Login
./cli/file_integrity_cli.py login

# Upload a file
./cli/file_integrity_cli.py upload /path/to/file.pdf

# List your files
./cli/file_integrity_cli.py list

# Verify a file
./cli/file_integrity_cli.py verify <file_id>

# Download a file
./cli/file_integrity_cli.py download <file_id> /path/to/save

# Logout
./cli/file_integrity_cli.py logout
```

### API Examples

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password123"}'

# Upload file
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  -F "password=your_password"

# Verify file
curl -X POST http://localhost:8000/api/v1/verify/<file_id> \
  -H "Authorization: Bearer <token>"
```

## 🔧 Configuration

### Environment Variables

```env
# MongoDB
MONGO_URI=mongodb://mongodb:27017/
DATABASE_NAME=file_integrity_db

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Encryption
MASTER_KEY=your-master-encryption-key-32bytes!!

# RabbitMQ
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672//

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# File Upload
MAX_FILE_SIZE_MB=100
```

## 📊 Monitoring

### System Health

```bash
# Get detailed system health
curl http://localhost:8000/health

# Get metrics (admin only)
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/api/v1/monitoring/metrics?hours=24
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/<user_id>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Webhooks

```bash
# Register webhook
curl -X POST http://localhost:8000/api/v1/webhooks/register \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://your-app.com/webhook","events":["file.uploaded","file.verified"]}'

# List webhooks
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/webhooks
```

## 🏗️ Development

### Project Structure

```
File Integrity & Authenticity Verification System/
├── cli/                    # CLI client
│   ├── client.py
│   └── file_integrity_cli.py
├── frontend/              # React web application
│   ├── index.html
│   ├── app.jsx
│   ├── admin-dashboard.jsx
│   ├── api.js
│   └── styles.css
├── gateway/               # FastAPI gateway
│   ├── main.py
│   ├── auth.py
│   ├── dependencies.py
│   ├── rate_limit.py
│   └── websocket_manager.py
├── services/              # Business logic services
│   ├── file_service.py
│   ├── auth_service.py
│   ├── crypto_service.py
│   ├── verification_service.py
│   ├── audit_service.py
│   ├── webhook_service.py
│   ├── monitoring_service.py
│   └── orchestrator.py
├── repositories/          # Data access layer
│   ├── file_repo.py
│   ├── user_repo.py
│   ├── key_repo.py
│   └── verification_repo.py
├── security/              # Cryptography modules
│   ├── hashing.py
│   ├── rsa.py
│   ├── aes_storage.py
│   └── jwt_utils.py
├── workers/               # Background task workers
│   ├── celery_app.py
│   └── tasks.py
├── storage/               # File storage
│   ├── files/
│   ├── keys/
│   └── signatures/
├── logs/                  # Application logs
├── config.py              # Configuration management
├── database.py            # Database connection
├── docker-compose.yml     # Docker orchestration
├── Dockerfile             # Container image
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Running Tests

```bash
# Run integration tests
python test_integration.py

# Run system tests
python test_system.py
```

## 🔒 Security

### Best Practices

1. **Change Default Credentials** - Update all default passwords in production
2. **Use Environment Variables** - Store sensitive data in `.env` file
3. **Enable HTTPS** - Use TLS/SSL in production
4. **Regular Updates** - Keep dependencies updated
5. **Audit Logs** - Monitor system activity regularly

### Cryptography

- **SHA-256**: File integrity hashing
- **RSA-2048**: Digital signatures
- **AES-256-GCM**: Symmetric encryption
- **PBKDF2**: Password hashing with bcrypt
- **JWT HS256**: Token authentication

## 📝 API Documentation

Full API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Nginx web server |
| Backend | 8000 | FastAPI application |
| MongoDB | 27017 | Database |
| RabbitMQ | 5672 | AMQP broker |
| RabbitMQ Management | 15672 | Management UI |
| Celery Worker | - | Background tasks |

## 📈 Performance

- Async file processing with Celery
- Rate limiting: 100 requests/minute (configurable)
- WebSocket connections for real-time updates
- Connection pooling for database
- Caching strategies for static content

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is proprietary and confidential.

## 👥 Support

For support and questions:
- Open an issue in the repository
- Contact the development team

## 🗺️ Roadmap

- [ ] Mobile application (iOS/Android)
- [ ] Batch file verification
- [ ] File versioning
- [ ] Advanced analytics dashboard
- [ ] Integration with cloud storage (S3, Azure Blob)
- [ ] Multi-tenancy support
- [ ] Compliance reporting (GDPR, HIPAA)

---

**Version**: 2.0.0  
**Last Updated**: February 2026
