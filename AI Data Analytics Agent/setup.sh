#!/bin/bash

# AI Data Analytics Agent Setup Script

echo "📊 Setting up AI Data Analytics Agent..."

# Run the universal Python setup
cd "$(dirname "$0")"
../setup_python_env.sh

# Additional project-specific setup if needed
echo "🔧 Performing Analytics-specific setup..."

# Activate the environment for additional setup
source .venv/bin/activate

# Install any additional analytics-specific dependencies
pip install streamlit plotly seaborn scikit-learn

# Create necessary directories
mkdir -p data/uploads
mkdir -p data/processed
mkdir -p logs

echo "📈 AI Data Analytics Agent is ready!"
echo ""
echo "📋 To start development:"
echo "   cd 'AI Data Analytics Agent'"
echo "   source .venv/bin/activate"
echo "   streamlit run streamlit_app.py"
echo ""
echo "🐳 To start with Docker:"
echo "   docker-compose up -d"
