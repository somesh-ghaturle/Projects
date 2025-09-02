#!/bin/bash

# Universal Python Project Setup Script
# This script creates a virtual environment and installs dependencies for any Python project

set -e  # Exit on any error

PROJECT_NAME=$(basename "$(pwd)")
VENV_DIR=".venv"
PYTHON_CMD="python3"

echo "🚀 Setting up Python environment for: $PROJECT_NAME"
echo "📍 Current directory: $(pwd)"

# Check if Python 3 is available
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

echo "🐍 Python version: $($PYTHON_CMD --version)"

# Remove existing virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    echo "🗑️  Removing existing virtual environment..."
    rm -rf "$VENV_DIR"
fi

# Create new virtual environment
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv "$VENV_DIR"

# Activate virtual environment
echo "⚡ Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install requirements if available
REQUIREMENTS_INSTALLED=false

# Check for production requirements first
if [ -f "requirements-production.txt" ]; then
    echo "📋 Installing production requirements..."
    pip install -r requirements-production.txt
    REQUIREMENTS_INSTALLED=true
elif [ -f "requirements.production.txt" ]; then
    echo "📋 Installing production requirements..."
    pip install -r requirements.production.txt
    REQUIREMENTS_INSTALLED=true
elif [ -f "requirements.txt" ]; then
    echo "📋 Installing requirements..."
    pip install -r requirements.txt
    REQUIREMENTS_INSTALLED=true
else
    echo "⚠️  No requirements.txt file found"
fi

# Install common development dependencies
echo "🛠️  Installing common development dependencies..."
pip install --upgrade pip setuptools wheel

# Show installed packages
echo "📦 Installed packages:"
pip list --format=columns

# Create activation instructions
echo ""
echo "✅ Setup complete!"
echo ""
echo "🎯 To activate this environment:"
echo "   source .venv/bin/activate"
echo ""
echo "🔧 To deactivate:"
echo "   deactivate"
echo ""
if [ "$REQUIREMENTS_INSTALLED" = true ]; then
    echo "📋 Dependencies installed successfully!"
else
    echo "⚠️  Remember to install your project dependencies manually"
fi

# Save environment info
echo "Environment created on: $(date)" > .venv/environment_info.txt
echo "Python version: $($PYTHON_CMD --version)" >> .venv/environment_info.txt
echo "Project: $PROJECT_NAME" >> .venv/environment_info.txt

echo "🎉 Virtual environment setup completed for $PROJECT_NAME!"
