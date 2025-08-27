#!/bin/bash

# AgenTech Research Hub - Docker Deployment Script
# ===============================================

set -e

echo "🚀 AgenTech Research Hub - Docker Deployment"
echo "============================================="

PROJECT_DIR="/Users/somesh/Library/CloudStorage/OneDrive-PaceUniversity/github/Projects/AgenTech Research Hub"
cd "$PROJECT_DIR"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before proceeding."
    echo "   You can continue with default settings for demo purposes."
    read -p "Press Enter to continue..."
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Health check
echo "🔍 Performing health checks..."

# Check API health
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ API Service: Healthy"
else
    echo "❌ API Service: Not responding"
fi

# Check Web UI
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Web UI: Accessible"
else
    echo "❌ Web UI: Not accessible"
fi

# Show container status
echo ""
echo "📊 Container Status:"
docker-compose ps

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "🌐 Web Interface: http://localhost:3000"
echo "🔗 API Endpoint: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "💡 To stop all services: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"
echo "🔧 To rebuild: docker-compose build --no-cache"
echo ""
echo "🤖 Your AgenTech Research Hub is ready with Web UI!"

# Open browser (optional)
if command -v open >/dev/null 2>&1; then
    echo ""
    read -p "🌐 Open web interface in browser? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open http://localhost:3000
    fi
fi
