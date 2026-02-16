# Docker Deployment Guide

## 🐳 Quick Start with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### One-Command Start

```bash
docker-compose up -d
```

This will start:
- **MongoDB** on port 27017
- **Backend API** on port 8000
- **Frontend** on port 3000

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📦 Container Services

### 1. MongoDB (Database)
- **Image**: mongo:7.0
- **Port**: 27017
- **Volumes**: Persistent data storage
- **Health Check**: Automatic ping check

### 2. Backend (FastAPI)
- **Build**: Custom Dockerfile
- **Port**: 8000
- **Dependencies**: Waits for MongoDB to be healthy
- **Volumes**: 
  - `./storage` - File storage
  - `./logs` - Application logs

### 3. Frontend (Nginx)
- **Image**: nginx:alpine
- **Port**: 3000
- **Features**: 
  - Serves static files
  - Proxies API requests to backend
  - Gzip compression enabled

## 🔧 Configuration

### Environment Variables

Copy `.env.docker` to `.env` and update:

```bash
cp .env.docker .env
```

**Important**: Change these values in production:
- `JWT_SECRET_KEY` - Use a strong random key
- `MASTER_KEY` - Use a 32-byte encryption key

### Generate Secure Keys

```bash
# JWT Secret (256-bit)
openssl rand -hex 32

# Master Encryption Key (256-bit)
openssl rand -hex 32
```

## 🚀 Docker Commands

### Start Services
```bash
docker-compose up -d
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f mongodb
docker-compose logs -f frontend
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

### Stop and Remove All (including volumes)
```bash
docker-compose down -v
```

## 🔍 Service Status

### Check Health
```bash
# All containers
docker-compose ps

# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/
```

### Access Container Shell
```bash
# Backend
docker exec -it file-integrity-backend bash

# MongoDB
docker exec -it file-integrity-mongodb mongosh
```

## 📊 Monitoring

### Resource Usage
```bash
docker stats
```

### Container Logs
```bash
# Real-time logs
docker-compose logs -f --tail=100

# Last 50 lines
docker-compose logs --tail=50
```

## 🔐 Security Best Practices

### Production Deployment

1. **Change Default Secrets**
   ```bash
   # Update .env file
   JWT_SECRET_KEY=<your-secure-key>
   MASTER_KEY=<your-encryption-key>
   ```

2. **Use Environment-Specific Configs**
   ```bash
   # Production
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

3. **Enable HTTPS** (use nginx-proxy or traefik)

4. **Limit Network Exposure**
   - Only expose necessary ports
   - Use internal networks for service communication

5. **Regular Updates**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## 🗄️ Data Persistence

### Backup MongoDB
```bash
# Create backup
docker exec file-integrity-mongodb mongodump --out=/tmp/backup

# Copy to host
docker cp file-integrity-mongodb:/tmp/backup ./mongodb-backup
```

### Restore MongoDB
```bash
# Copy backup to container
docker cp ./mongodb-backup file-integrity-mongodb:/tmp/backup

# Restore
docker exec file-integrity-mongodb mongorestore /tmp/backup
```

### Backup Uploaded Files
```bash
# Files are in ./storage directory
tar -czf storage-backup-$(date +%Y%m%d).tar.gz storage/
```

## 🐛 Troubleshooting

### Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Verify MongoDB is healthy
docker-compose ps mongodb
```

### Frontend Can't Connect to Backend
```bash
# Check nginx config
docker exec file-integrity-frontend cat /etc/nginx/conf.d/default.conf

# Test backend from frontend container
docker exec file-integrity-frontend wget -O- http://backend:8000/health
```

### MongoDB Connection Issues
```bash
# Test MongoDB connectivity
docker exec file-integrity-backend python -c "from pymongo import MongoClient; print(MongoClient('mongodb://mongodb:27017/').server_info())"
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill process or change port in docker-compose.yml
```

## 🔄 Development Workflow

### Live Code Reload (Development)

Create `docker-compose.dev.yml`:
```yaml
version: '3.8'
services:
  backend:
    command: python -m uvicorn gateway.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
```

Run:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 📝 Production Checklist

- [ ] Update all secret keys in `.env`
- [ ] Configure HTTPS/SSL certificates
- [ ] Set up automated backups
- [ ] Configure monitoring/alerting
- [ ] Enable firewall rules
- [ ] Set resource limits (CPU/Memory)
- [ ] Configure log rotation
- [ ] Set up container orchestration (K8s/Swarm)
- [ ] Implement CI/CD pipeline
- [ ] Configure reverse proxy (nginx/traefik)

## 🌐 Scaling

### Horizontal Scaling (Multiple Backend Instances)

```yaml
services:
  backend:
    deploy:
      replicas: 3
```

### Load Balancing
Use nginx or HAProxy to distribute traffic across backend instances.

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MongoDB Docker](https://hub.docker.com/_/mongo)
- [Nginx Docker](https://hub.docker.com/_/nginx)
