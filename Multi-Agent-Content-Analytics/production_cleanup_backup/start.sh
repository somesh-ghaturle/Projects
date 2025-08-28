#!/bin/bash

echo "🚀 Starting Multi-Agent Content Analytics..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the application
echo "🔨 Building and starting containers..."
docker-compose up --build -d

# Wait for the service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 10

# Check if the service is running
echo "🔍 Checking service status..."
if curl -s http://localhost:8001/ > /dev/null; then
    echo "✅ Multi-Agent Content Analytics is running!"
    echo "📍 API available at: http://localhost:8001"
    echo "📍 Web Interface at: http://localhost:8001/web"
    echo "📍 API Documentation at: http://localhost:8001/docs"
    echo ""
    echo "🤖 Available Agents:"
    echo "  - Script Summarizer: /agent/script_summarizer"
    echo "  - Genre Classifier: /agent/genre_classifier" 
    echo "  - Marketing Agent: /agent/marketing_agent"
    echo ""
    echo "📊 Container Status:"
    docker-compose ps
else
    echo "❌ Service failed to start. Checking logs..."
    docker-compose logs
fi
