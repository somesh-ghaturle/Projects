#!/bin/bash

# MedAssist AI MCP Setup Script

echo "🏥 Setting up MedAssist AI MCP..."

# Run the universal Python setup
cd "$(dirname "$0")"
../setup_python_env.sh

# Additional project-specific setup if needed
echo "🔧 Performing Medical AI-specific setup..."

# Activate the environment for additional setup
source .venv/bin/activate

# Install any additional medical AI-specific dependencies
pip install biopython transformers torch

# Create necessary directories
mkdir -p data/medical
mkdir -p vector-db/data
mkdir -p logs

echo "🩺 MedAssist AI MCP is ready!"
echo ""
echo "📋 To start development:"
echo "   cd 'MedAssist Al MCP'"
echo "   source .venv/bin/activate"
echo "   # Run your medical AI application"
echo ""
echo "🐳 To start with Docker:"
echo "   docker-compose up -d"
