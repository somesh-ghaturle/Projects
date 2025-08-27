#!/bin/bash
# Docker Test Script - Test API Connection in Docker

echo "🚀 Starting AgenTech Research Hub Docker Test..."

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down

# Remove old images to ensure fresh build
echo "Removing old images..."
docker rmi agentech-research-hub-agentech-api 2>/dev/null || true

# Build and start services
echo "Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 15

# Test API health
echo "Testing API health..."
curl -f http://localhost:8000/health || echo "❌ Direct API connection failed"

# Test Web UI
echo "Testing Web UI..."
curl -f http://localhost:3000 > /dev/null && echo "✅ Web UI accessible" || echo "❌ Web UI failed"

# Test API through nginx proxy
echo "Testing API through nginx proxy..."
curl -f http://localhost:3000/health && echo "✅ Nginx proxy working" || echo "❌ Nginx proxy failed"

# Show container status
echo "Container status:"
docker-compose ps

# Show logs for debugging
echo "API logs:"
docker-compose logs agentech-api | tail -10

echo "WebUI logs:"
docker-compose logs agentech-webui | tail -5

echo "🏁 Test complete! Access the UI at: http://localhost:3000"
