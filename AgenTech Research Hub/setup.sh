#!/bin/bash

# AgenTech Research Hub Setup Script

echo "🔬 Setting up AgenTech Research Hub..."

# Run the universal Python setup
cd "$(dirname "$0")"
../setup_python_env.sh

# Additional project-specific setup if needed
echo "🔧 Performing AgenTech-specific setup..."

# Activate the environment for additional setup
source .venv/bin/activate

# Install any additional dependencies specific to AgenTech
pip install crewai crewai-tools

# Create necessary directories
mkdir -p logs/nginx
mkdir -p data
mkdir -p temp

echo "🎯 AgenTech Research Hub is ready!"
echo ""
echo "📋 To start development:"
echo "   cd 'AgenTech Research Hub'"
echo "   source .venv/bin/activate"
echo "   python agentech_api_server.py"
echo ""
echo "🐳 To start with Docker:"
echo "   docker-compose up -d"
