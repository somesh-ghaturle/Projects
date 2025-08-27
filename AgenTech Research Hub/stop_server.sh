#!/bin/bash

# AgenTech Research Hub - Stop Server Script
# ==========================================

echo "🛑 Stopping AgenTech Research Hub..."
echo "===================================="

# Find and kill the API server process
if pgrep -f "python api_server.py" > /dev/null; then
    echo "🔍 Found running server process..."
    pkill -f "python api_server.py"
    echo "✅ Server stopped successfully"
    
    # Wait a moment for cleanup
    sleep 2
    
    # Verify it's stopped
    if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Confirmed: Server is no longer responding"
    else
        echo "⚠️  Server may still be running - check manually"
    fi
else
    echo "ℹ️  No running server found"
fi

echo ""
echo "🔧 To restart the server: ./start_server.sh"
