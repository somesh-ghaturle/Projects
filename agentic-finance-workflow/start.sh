#!/bin/bash

# Agentic Finance Workflow - Quick Start Script
# This script starts both the API server and web interface

echo "🚀 Starting Agentic Finance Workflow..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start API server with Docker
echo "📡 Starting API server..."
docker-compose up -d

# Wait a moment for the server to start
sleep 3

# Check if API is healthy
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ API server is running on http://localhost:8001"
else
    echo "❌ API server failed to start"
    exit 1
fi

# Start web interface
echo "🌐 Starting web interface..."
echo "📱 Opening browser to http://localhost:3001/web_interface.html"
echo ""
echo "🎯 Ready! You can now:"
echo "   • Analyze stocks with individual agents"
echo "   • Run complete financial workflows"
echo "   • View real-time results"
echo ""
echo "Press Ctrl+C to stop the web interface"
echo "To stop the API server: docker-compose down"
echo ""

# Start the web interface server
python3 start_ui_server.py
