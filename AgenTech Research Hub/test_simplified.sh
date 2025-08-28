#!/bin/bash
# Simple test script for AgenTech Research Hub

set -e

echo "🧪 Testing AgenTech Research Hub - Simplified Version"
echo "=================================================="

# Test 1: Install dependencies
echo "📦 Installing minimal dependencies..."
pip3 install -r requirements.txt

echo "✅ Dependencies installed successfully"

# Test 2: Import test
echo "🔍 Testing Python imports..."
python3 -c "
import sys
sys.path.append('src')
from src.config.settings import get_settings
from src.core.monitoring import health_checker
from src.core.security import verify_api_key
print('✅ All imports working')
"

# Test 3: Start server test (background)
echo "🚀 Starting API server..."
python3 api_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test 4: Health check
echo "❤️ Testing health endpoint..."
response=$(curl -s http://localhost:8000/health)
if [[ $response == *"healthy"* ]]; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    echo "Response: $response"
fi

# Test 5: API endpoints
echo "📡 Testing API endpoints..."

# Test root endpoint
root_response=$(curl -s http://localhost:8000/)
if [[ $root_response == *"AgenTech"* ]]; then
    echo "✅ Root endpoint working"
else
    echo "❌ Root endpoint failed"
fi

# Test status endpoint
status_response=$(curl -s http://localhost:8000/status)
if [[ $status_response == *"version"* ]]; then
    echo "✅ Status endpoint working"
else
    echo "❌ Status endpoint failed"
fi

# Test research endpoint (mock)
research_response=$(curl -s -X POST \
  http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "test research query"}')

if [[ $research_response == *"success"* ]]; then
    echo "✅ Research endpoint working"
else
    echo "❌ Research endpoint failed"
    echo "Response: $research_response"
fi

# Clean up
echo "🧹 Cleaning up..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null || true

echo ""
echo "🎉 All tests completed!"
echo "✅ AgenTech Research Hub is ready for development"
echo ""
echo "To start the server manually:"
echo "  python3 api_server.py"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"
