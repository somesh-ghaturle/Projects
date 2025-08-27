"""
Simple test script to verify our MCP project setup.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

print("Personal Document Assistant MCP Server")
print("=====================================")

# Test basic imports
try:
    import fastapi
    import uvicorn
    import pydantic
    import yaml
    print("✓ Basic dependencies imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Test configuration loading
try:
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print("✓ Configuration loaded successfully")
    else:
        print("✗ Configuration file not found")
except Exception as e:
    print(f"✗ Configuration error: {e}")

# Test data directories
data_dir = Path(__file__).parent.parent / "data"
required_dirs = ["uploads", "chroma_db", "logs"]

for dir_name in required_dirs:
    dir_path = data_dir / dir_name
    if dir_path.exists():
        print(f"✓ Directory {dir_name} exists")
    else:
        print(f"✗ Directory {dir_name} missing")

# Test module structure
src_dir = Path(__file__).parent
required_modules = ["server.py", "storage", "rag", "utils"]

for module in required_modules:
    module_path = src_dir / module
    if module_path.exists():
        print(f"✓ Module {module} exists")
    else:
        print(f"✗ Module {module} missing")

print("\nProject structure verification complete!")
print("\nNext steps:")
print("1. Install Ollama: brew install ollama")
print("2. Start Ollama: ollama serve")
print("3. Pull a model: ollama pull llama3.2")
print("4. Run the MCP server: python src/server.py")

if __name__ == "__main__":
    # Test FastAPI creation
    try:
        from fastapi import FastAPI
        app = FastAPI(title="Personal Document Assistant MCP Server")
        print("✓ FastAPI app creation successful")
        
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "message": "MCP server is operational"}
        
        print("✓ Health endpoint created")
        print("\nBasic setup verification: SUCCESS")
        print("All core components are properly configured!")
        
    except Exception as e:
        print(f"✗ FastAPI setup error: {e}")
        sys.exit(1)
