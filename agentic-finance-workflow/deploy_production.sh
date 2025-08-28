#!/bin/bash
# Production deployment script for Agentic Finance Workflow

set -e

echo "🚀 Starting Agentic Finance Workflow Production Deployment"
echo "============================================================"

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p logs data nginx/ssl

# Set proper permissions
echo "🔒 Setting permissions..."
chmod 755 logs data
chmod 644 nginx/nginx.conf

# Build and start containers
echo "🐳 Building and starting containers..."
docker-compose -f docker-compose.production.yml down --remove-orphans
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check health
echo "💚 Checking service health..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Services are healthy!"
else
    echo "❌ Health check failed. Checking logs..."
    docker-compose -f docker-compose.production.yml logs --tail=50
    exit 1
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo "============================================================"
echo "📡 API Server: http://localhost"
echo "📚 API Documentation: http://localhost/api/docs"
echo "💚 Health Check: http://localhost/health"
echo "📊 Agent Status: http://localhost/agents"
echo ""
echo "🐳 Container Status:"
docker-compose -f docker-compose.production.yml ps
echo ""
echo "📝 To view logs: docker-compose -f docker-compose.production.yml logs -f"
echo "🛑 To stop: docker-compose -f docker-compose.production.yml down"
