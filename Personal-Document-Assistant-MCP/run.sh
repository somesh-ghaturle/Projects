#!/bin/bash

# Personal Document Assistant MCP Server Startup Script

echo "🚀 Starting Personal Document Assistant MCP Server..."

# Check if we're in the right directory
if [ ! -f "src/server.py" ]; then
    echo "❌ Error: Must run from project root directory"
    exit 1
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Run setup first."
    exit 1
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is running
echo "🤖 Checking Ollama connection..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Error: Ollama is not running. Please start Ollama first:"
    echo "   brew services start ollama"
    echo "   # or"
    echo "   ollama serve"
    exit 1
fi

# Create necessary directories
mkdir -p logs data/uploads data/chroma_db

# Start the server
echo "✅ Starting MCP server..."
cd src
python server.py
