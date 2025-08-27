"""
Basic tests to verify the project structure and configuration
"""
import pytest
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_project_structure():
    """Test that the project has the expected structure"""
    base_dir = Path(__file__).parent.parent
    
    # Check main directories exist
    assert (base_dir / "src").exists()
    assert (base_dir / "tests").exists()
    assert (base_dir / "README.md").exists()
    assert (base_dir / "requirements.txt").exists()
    assert (base_dir / ".env.example").exists()
    
    # Check src subdirectories
    src_dir = base_dir / "src"
    assert (src_dir / "agents").exists()
    assert (src_dir / "api").exists()
    assert (src_dir / "data").exists()
    assert (src_dir / "ml").exists()
    assert (src_dir / "utils").exists()

def test_config_file_exists():
    """Test that configuration files exist"""
    base_dir = Path(__file__).parent.parent
    
    config_file = base_dir / "src" / "config.py"
    assert config_file.exists()
    
    # Try to import config (should work without external dependencies)
    try:
        from config import Config
        assert hasattr(Config, 'OPENAI_API_KEY')
        assert hasattr(Config, 'DATABASE_URL')
    except ImportError as e:
        # This is expected if dependencies aren't installed
        print(f"Config import failed (expected): {e}")

def test_requirements_file():
    """Test that requirements.txt contains expected packages"""
    base_dir = Path(__file__).parent.parent
    requirements_file = base_dir / "requirements.txt"
    
    assert requirements_file.exists()
    
    content = requirements_file.read_text()
    
    # Check for core packages
    assert "fastapi" in content
    assert "uvicorn" in content
    assert "pytest" in content
    assert "pydantic" in content

def test_env_example():
    """Test that .env.example has required variables"""
    base_dir = Path(__file__).parent.parent
    env_file = base_dir / ".env.example"
    
    assert env_file.exists()
    
    content = env_file.read_text()
    
    # Check for required environment variables
    assert "OPENAI_API_KEY" in content
    assert "DATABASE_URL" in content
    assert "REDIS_URL" in content

def test_readme_has_content():
    """Test that README.md has substantial content"""
    base_dir = Path(__file__).parent.parent
    readme_file = base_dir / "README.md"
    
    assert readme_file.exists()
    
    content = readme_file.read_text()
    
    # Check README has substantial content (should be our comprehensive documentation)
    assert len(content) > 1000  # Should be quite large with all the Mermaid diagrams
    assert "Multi-Agent AI System for Content Analytics" in content
    assert "mermaid" in content.lower()  # Should have Mermaid diagrams

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
