"""
Application settings and configuration
"""
import os
from typing import List


class Settings:
    """Application settings class"""
    
    # App information
    app_name: str = "AgenTech Research Hub"
    app_version: str = "1.0.0"
    app_description: str = "AI-powered research and analysis platform"
    app_environment: str = os.getenv("APP_ENVIRONMENT", "development")
    
    # API configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Security
    enable_api_key_auth: bool = os.getenv("ENABLE_API_KEY_AUTH", "false").lower() == "true"
    
    # CORS settings
    cors_allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000"
    ]
    
    # Feature flags
    enable_web_scraping: bool = os.getenv("ENABLE_WEB_SCRAPING", "true").lower() == "true"
    enable_academic_search: bool = os.getenv("ENABLE_ACADEMIC_SEARCH", "true").lower() == "true"
    enable_news_search: bool = os.getenv("ENABLE_NEWS_SEARCH", "true").lower() == "true"


# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get the global settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
