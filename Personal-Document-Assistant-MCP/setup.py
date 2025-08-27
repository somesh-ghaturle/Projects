#!/usr/bin/env python3
"""
Setup script for Personal Document Assistant MCP Server
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0 and check:
        print(f"Error running command: {command}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    
    return result


def check_python_version():
    """Check Python version."""
    if sys.version_info < (3, 9):
        print("Python 3.9 or higher is required.")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def create_virtual_environment():
    """Create a virtual environment."""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✓ Virtual environment already exists")
        return
    
    print("Creating virtual environment...")
    run_command(f"{sys.executable} -m venv venv")
    print("✓ Virtual environment created")


def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    
    # Determine the correct pip path
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    # Upgrade pip first
    run_command(f"{pip_path} install --upgrade pip")
    
    # Install dependencies
    run_command(f"{pip_path} install -r requirements.txt")
    print("✓ Dependencies installed")


def create_data_directories():
    """Create necessary data directories."""
    directories = [
        "data",
        "data/vectordb",
        "data/documents",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def copy_config_template():
    """Copy configuration template."""
    config_file = Path("config/settings.yaml")
    
    if config_file.exists():
        print("✓ Configuration file already exists")
        return
    
    # The config file should already exist from our setup
    if config_file.exists():
        print("✓ Configuration template ready")
        print("  Please edit config/settings.yaml with your API keys and preferences")
    else:
        print("⚠ Configuration template not found. Please create config/settings.yaml")


def check_docker():
    """Check if Docker is available."""
    try:
        result = run_command("docker --version", check=False)
        if result.returncode == 0:
            print("✓ Docker is available")
            return True
        else:
            print("⚠ Docker not found. Docker deployment will not be available.")
            return False
    except:
        print("⚠ Docker not found. Docker deployment will not be available.")
        return False


def setup_development_environment():
    """Set up development tools."""
    print("Setting up development environment...")
    
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip"
    else:
        pip_path = "venv/bin/pip"
    
    # Install development dependencies
    dev_deps = [
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "black>=23.11.0",
        "flake8>=6.1.0",
        "isort>=5.12.0"
    ]
    
    for dep in dev_deps:
        run_command(f"{pip_path} install {dep}")
    
    print("✓ Development environment set up")


def create_vscode_settings():
    """Create VS Code settings for the project."""
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    settings = {
        "python.defaultInterpreterPath": "./venv/bin/python" if sys.platform != "win32" else ".\\venv\\Scripts\\python.exe",
        "python.terminal.activateEnvironment": True,
        "python.formatting.provider": "black",
        "python.linting.enabled": True,
        "python.linting.flake8Enabled": True,
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            "**/venv": True,
            "**/data": True
        }
    }
    
    import json
    with open(vscode_dir / "settings.json", "w") as f:
        json.dump(settings, f, indent=2)
    
    print("✓ VS Code settings created")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    
    print("\nNext steps:")
    print("1. Edit config/settings.yaml with your API keys:")
    print("   - OpenAI API key (if using OpenAI)")
    print("   - Anthropic API key (if using Anthropic)")
    
    print("\n2. Activate the virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n3. Run the MCP server:")
    print("   python src/server.py")
    
    print("\n4. Test the installation:")
    print("   pytest tests/")
    
    print("\n5. For deployment:")
    print("   - Local: python src/server.py")
    print("   - Docker: docker-compose -f docker/docker-compose.yml up")
    print("   - Cloud: Push to Railway/Render and deploy")
    
    print("\nDocumentation:")
    print("- README.md - Full documentation")
    print("- config/settings.yaml - Configuration options")
    print("- docs/ - Additional documentation")


def main():
    """Main setup function."""
    print("Personal Document Assistant MCP Server Setup")
    print("=" * 45)
    
    try:
        # Check prerequisites
        check_python_version()
        
        # Set up Python environment
        create_virtual_environment()
        install_dependencies()
        
        # Set up project structure
        create_data_directories()
        copy_config_template()
        
        # Set up development environment
        setup_development_environment()
        create_vscode_settings()
        
        # Check optional tools
        check_docker()
        
        # Print next steps
        print_next_steps()
        
    except KeyboardInterrupt:
        print("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
