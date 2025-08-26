"""
Test configuration and fixtures
"""

import pytest
import asyncio
from pathlib import Path

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_data():
    """Sample data for testing"""
    return {
        "text": "This is a sample text for testing",
        "numbers": [1, 2, 3, 4, 5],
        "config": {
            "enabled": True,
            "threshold": 0.5
        }
    }


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for testing"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Sample content for testing")
    return file_path
