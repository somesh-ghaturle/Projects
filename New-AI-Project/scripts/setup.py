#!/usr/bin/env python3
"""
Setup script for the New AI Project
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("Virtual environment created successfully")
    else:
        print("Virtual environment already exists")

def install_dependencies():
    """Install project dependencies"""
    print("Installing dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip"
    else:  # macOS/Linux
        pip_path = "venv/bin/pip"
    
    # Install dependencies
    if not run_command(f"{pip_path} install -r requirements.txt"):
        print("Failed to install dependencies")
        return False
    
    print("Dependencies installed successfully")
    return True

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file from .env.example...")
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            dst.write(src.read())
        print(".env file created. Please update it with your actual values.")
    else:
        print(".env file already exists or .env.example not found")

def create_data_directories():
    """Create necessary data directories"""
    directories = [
        "data/raw",
        "data/processed", 
        "data/models",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        # Create .gitkeep files
        gitkeep = Path(directory) / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()
    
    print("Data directories created")

def main():
    """Main setup function"""
    print("Setting up New AI Project...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Change to project directory
    script_dir = Path(__file__).parent.parent
    os.chdir(script_dir)
    
    try:
        # Setup steps
        create_virtual_environment()
        install_dependencies()
        create_env_file()
        create_data_directories()
        
        print("\n" + "=" * 50)
        print("Setup completed successfully!")
        print("\nNext steps:")
        print("1. Activate virtual environment:")
        if os.name == 'nt':
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print("2. Update .env file with your configuration")
        print("3. Run the application:")
        print("   python src/main.py")
        
    except Exception as e:
        print(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
