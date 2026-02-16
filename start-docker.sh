#!/bin/bash

# File Integrity & Authenticity Verification Platform - Docker Quick Start

set -e

echo "🔐 File Integrity & Authenticity Verification Platform"
echo "======================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is installed"
echo -e "${GREEN}✓${NC} Docker Compose is installed"
echo ""

# Generate .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚙${NC}  Generating .env file with secure keys..."
    cp .env.docker .env
    
    # Generate secure keys (if openssl is available)
    if command -v openssl &> /dev/null; then
        JWT_SECRET=$(openssl rand -hex 32)
        MASTER_KEY=$(openssl rand -hex 32)
        
        # Update .env file
        sed -i.bak "s/change-this-to-a-secure-random-secret-key-in-production/$JWT_SECRET/" .env
        sed -i.bak "s/change-this-to-a-32-byte-secure-key-for-production-use/$MASTER_KEY/" .env
        rm .env.bak 2>/dev/null || true
        
        echo -e "${GREEN}✓${NC} Secure keys generated"
    else
        echo -e "${YELLOW}⚠${NC}  OpenSSL not found. Please update JWT_SECRET_KEY and MASTER_KEY in .env manually"
    fi
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

echo ""
echo -e "${BLUE}🚀 Starting services...${NC}"
echo ""

# Build and start services
docker-compose up -d --build

echo ""
echo -e "${GREEN}✓${NC} Services started successfully!"
echo ""

# Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
sleep 5

# Check service status
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo -e "${GREEN}✅ Application is ready!${NC}"
echo ""
echo "🌐 Access the application:"
echo "   Frontend:         http://localhost:3000"
echo "   Backend API:      http://localhost:8000"
echo "   API Docs:         http://localhost:8000/docs"
echo "   Health Check:     http://localhost:8000/health"
echo ""
echo "📝 Useful commands:"
echo "   View logs:        docker-compose logs -f"
echo "   Stop services:    docker-compose down"
echo "   Restart:          docker-compose restart"
echo "   Rebuild:          docker-compose up -d --build"
echo ""
echo "📚 Documentation:"
echo "   Docker Guide:     cat DOCKER_README.md"
echo "   Main README:      cat README.md"
echo ""

# Open browser (optional)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    read -p "Open browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:3000
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    read -p "Open browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        xdg-open http://localhost:3000 2>/dev/null || true
    fi
fi

echo -e "${GREEN}🎉 Happy verifying!${NC}"
