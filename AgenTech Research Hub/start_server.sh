#!/bin/bash

# AgenTech Research Hub - Quick Deployment Script
# ===============================================

set -e  # Exit on any error

PROJECT_DIR="/Users/somesh/Library/CloudStorage/OneDrive-PaceUniversity/github/Projects/AgenTech Research Hub"

echo "🚀 Starting AgenTech Research Hub Deployment..."
echo "================================================"

# Navigate to project directory
cd "$PROJECT_DIR"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Set Python path
export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

# Check if server is already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Server is already running on port 8000"
    echo "   Use './stop_server.sh' to stop the current instance"
    exit 1
fi

# Start the server in background
echo "🚀 Starting API server..."
nohup python api_server.py > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to initialize..."
sleep 3

# Verify deployment
echo "🔍 Verifying deployment..."
if python deployment_verification.py; then
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "========================="
    echo "📡 API Server: http://localhost:8000"
    echo "📚 Documentation: http://localhost:8000/docs"
    echo "📊 Health Check: http://localhost:8000/health"
    echo "🔍 Research API: http://localhost:8000/research"
    echo ""
    echo "💡 To stop the server: ./stop_server.sh"
    echo "📝 View logs: tail -f server.log"
    echo ""
    echo "🤖 Your AgenTech Research Hub is ready!"
else
    echo "❌ Deployment verification failed"
    echo "📝 Check server.log for details"
    exit 1
fi
