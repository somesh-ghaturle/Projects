#!/bin/bash

echo "🚀 Starting Multi-Agent Content Analytics in PRODUCTION mode..."

# First run the cleanup script to ensure no unnecessary files
if [ -f "./cleanup_for_production.sh" ]; then
  echo "🧹 Running cleanup script first..."
  ./cleanup_for_production.sh
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start the application with the production configuration
echo "🔨 Building and starting production containers..."
docker-compose -f docker-compose.production.yml up --build -d

# Wait for the service to be ready
echo "⏳ Waiting for service to be ready..."
sleep 15

# Check if the service is running
echo "🔍 Checking service status..."
if curl -s http://localhost:8001/health | grep -q "healthy"; then
    echo "✅ Multi-Agent Content Analytics is running in PRODUCTION mode!"
    echo "📍 API available at: http://localhost:8001"
    echo "📍 Web Interface at: http://localhost:8001/web"
    echo "📍 API Documentation at: http://localhost:8001/docs"
    echo ""
    echo "🤖 Available Agents:"
    echo "  - Script Analyzer: /agent/script_analyzer"
    echo "  - Genre Classifier: /agent/genre_classifier" 
    echo "  - Marketing Agent: /agent/marketing_agent"
    echo ""
    echo "📊 Container Status:"
    docker-compose -f docker-compose.production.yml ps
else
    echo "❌ Service failed to start. Checking logs..."
    docker-compose -f docker-compose.production.yml logs
fi
