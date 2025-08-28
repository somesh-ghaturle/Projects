#!/bin/bash
# Start AgenTech Research Hub in Development Mode

set -e

echo "🚀 Starting AgenTech Research Hub - Development Mode"
echo "=================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "📦 Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if API is healthy
echo "❤️ Checking API health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API failed to start properly"
        docker-compose logs agentech-api
        exit 1
    fi
    sleep 2
done

# Check if Nginx is serving the UI
echo "🌐 Checking web interface..."
if curl -s http://localhost:80 > /dev/null; then
    echo "✅ Web interface is ready!"
else
    echo "⚠️ Web interface might not be ready yet"
fi

echo ""
echo "🎉 AgenTech Research Hub is now running!"
echo "📱 Web Interface: http://localhost"
echo "🔧 API Server: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "❤️ Health Check: http://localhost:8000/health"
echo ""
echo "To stop the services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f"
