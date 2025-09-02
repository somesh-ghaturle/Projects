#!/bin/bash

# Multi-Agent Content Analytics Setup Script

echo "📝 Setting up Multi-Agent Content Analytics..."

# Run the universal Python setup
cd "$(dirname "$0")"
../setup_python_env.sh

# Additional project-specific setup if needed
echo "🔧 Performing Content Analytics-specific setup..."

# Activate the environment for additional setup
source .venv/bin/activate

# Install any additional content analytics-specific dependencies
pip install nltk spacy textblob

# Create necessary directories
mkdir -p cache/content
mkdir -p logs/analytics
mkdir -p app/data

echo "📄 Multi-Agent Content Analytics is ready!"
echo ""
echo "📋 To start development:"
echo "   cd 'Multi-Agent-Content-Analytics'"
echo "   source .venv/bin/activate"
echo "   python multi_agent_content_api.py"
echo ""
echo "🐳 To start with Docker:"
echo "   docker-compose up -d"
