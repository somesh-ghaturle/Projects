#!/bin/bash

# Agentic Finance Workflow Setup Script

echo "💰 Setting up Agentic Finance Workflow..."

# Run the universal Python setup
cd "$(dirname "$0")"
../setup_python_env.sh

# Additional project-specific setup if needed
echo "🔧 Performing Finance-specific setup..."

# Activate the environment for additional setup
source .venv/bin/activate

# Install any additional finance-specific dependencies
pip install yfinance pandas-ta plotly streamlit

# Create necessary directories
mkdir -p static/charts
mkdir -p data/financial
mkdir -p logs

echo "💹 Agentic Finance Workflow is ready!"
echo ""
echo "📋 To start development:"
echo "   cd 'agentic-finance-workflow'"
echo "   source .venv/bin/activate"
echo "   python agentic_finance_api.py"
echo ""
echo "🐳 To start with Docker:"
echo "   docker-compose up -d"
