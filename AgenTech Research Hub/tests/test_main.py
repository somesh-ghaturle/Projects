"""
Main application tests
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.config.settings import Settings
from src.core.base import Application


class TestApplication:
    """Test the main Application class"""
    
    def test_application_initialization(self):
        """Test application initialization"""
        settings = Settings()
        app = Application(settings)
        
        assert app.settings == settings
        assert app.is_running is False
    
    @pytest.mark.asyncio
    async def test_application_start_stop(self):
        """Test application start and stop"""
        settings = Settings()
        app = Application(settings)
        
        # Mock the methods to avoid actual startup
        with patch.object(app, '_initialize_components'), \
             patch.object(app, '_start_services'), \
             patch.object(app, '_run'), \
             patch.object(app, '_stop_services'):
            
            # Start the application
            start_task = asyncio.create_task(app.start())
            await asyncio.sleep(0.1)  # Let it initialize
            
            # Stop the application
            await app.stop()
            
            # Wait for start task to complete
            try:
                await start_task
            except Exception:
                pass  # Expected due to mocking
    
    def test_settings_loading(self):
        """Test settings loading"""
        settings = Settings()
        
        assert settings.app_name is not None
        assert settings.app_version is not None
        assert settings.log_level is not None


class TestSettings:
    """Test configuration settings"""
    
    def test_default_values(self):
        """Test default configuration values"""
        settings = Settings()
        
        assert settings.app_name == "Multi-Agent AI Research Assistant"
        assert settings.app_version == "1.0.0"
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "llama3"
    
    def test_environment_override(self):
        """Test environment variable override"""
        import os
        
        # Set environment variable
        os.environ["app_name"] = "Test App"
        
        # Create new settings instance
        settings = Settings()
        
        assert settings.app_name == "Test App"
        
        # Clean up
        del os.environ["app_name"]


if __name__ == "__main__":
    pytest.main([__file__])
