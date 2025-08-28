"""
Core Configuration Module - Multi-Agent Content Analytics Platform

This module contains core configuration settings, constants, and system-wide
parameters for the Content Analytics Platform. It provides centralized
configuration management and environment-specific settings.

Author: Content Analytics Team
Version: 3.0.0
Last Updated: August 2025
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

class Environment(Enum):
    """Application environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(Enum):
    """Logging level configurations"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    version: str
    enabled: bool
    max_processing_time: float
    memory_limit_mb: int
    cache_results: bool

@dataclass
class APIConfig:
    """API configuration settings"""
    host: str
    port: int
    debug: bool
    cors_enabled: bool
    rate_limit_requests: int
    rate_limit_window_seconds: int
    max_content_length: int

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    pool_size: int
    max_overflow: int
    pool_timeout: int
    enable_logging: bool

class ContentAnalyticsConfig:
    """
    Main Configuration Class for Content Analytics Platform
    
    Provides centralized configuration management with environment-specific
    settings and runtime configuration options.
    """
    
    def __init__(self, environment: Environment = Environment.DEVELOPMENT):
        """
        Initialize configuration based on environment
        
        Args:
            environment (Environment): Target environment for configuration
        """
        self.environment = environment
        self._load_environment_variables()
        self._setup_logging_config()
        self._setup_agent_configs()
        self._setup_api_config()
        self._setup_database_config()
        self._setup_cache_config()
        self._setup_security_config()

    def _load_environment_variables(self):
        """Load and validate environment variables"""
        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///content_analytics.db")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.API_HOST = os.getenv("API_HOST", "0.0.0.0")
        self.API_PORT = int(os.getenv("API_PORT", "8000"))
        self.DEBUG_MODE = os.getenv("DEBUG", "true").lower() == "true"
        
        # External service configurations
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
        self.HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
        
        # Analytics and monitoring
        self.ANALYTICS_ENABLED = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"
        self.MONITORING_ENDPOINT = os.getenv("MONITORING_ENDPOINT")

    def _setup_logging_config(self):
        """Setup logging configuration"""
        log_level_map = {
            Environment.DEVELOPMENT: LogLevel.DEBUG,
            Environment.TESTING: LogLevel.INFO,
            Environment.STAGING: LogLevel.WARNING,
            Environment.PRODUCTION: LogLevel.ERROR
        }
        
        self.LOG_LEVEL = log_level_map.get(self.environment, LogLevel.INFO)
        self.LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.LOG_FILE = f"logs/content_analytics_{self.environment.value}.log"
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

    def _setup_agent_configs(self):
        """Setup individual agent configurations"""
        base_config = {
            "max_processing_time": 30.0,  # seconds
            "memory_limit_mb": 512,
            "cache_results": True
        }
        
        self.AGENT_CONFIGS = {
            "script_analyzer": AgentConfig(
                name="Script Analyzer",
                version="3.0.0",
                enabled=True,
                max_processing_time=45.0,  # Longer for complex analysis
                memory_limit_mb=1024,      # More memory for large scripts
                cache_results=True
            ),
            "genre_classifier": AgentConfig(
                name="Genre Classifier",
                version="3.0.0",
                enabled=True,
                max_processing_time=20.0,
                memory_limit_mb=512,
                cache_results=True
            ),
            "marketing_insights": AgentConfig(
                name="Marketing Insights",
                version="3.0.0",
                enabled=True,
                max_processing_time=35.0,  # Complex marketing analysis
                memory_limit_mb=768,
                cache_results=True
            )
        }

    def _setup_api_config(self):
        """Setup API configuration"""
        rate_limits = {
            Environment.DEVELOPMENT: (1000, 3600),  # 1000 requests per hour
            Environment.TESTING: (500, 3600),
            Environment.STAGING: (100, 3600),
            Environment.PRODUCTION: (50, 3600)       # 50 requests per hour in prod
        }
        
        rate_limit_requests, rate_limit_window = rate_limits.get(
            self.environment, (100, 3600)
        )
        
        self.API_CONFIG = APIConfig(
            host=self.API_HOST,
            port=self.API_PORT,
            debug=self.DEBUG_MODE and self.environment == Environment.DEVELOPMENT,
            cors_enabled=True,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window_seconds=rate_limit_window,
            max_content_length=1048576  # 1MB max content size
        )

    def _setup_database_config(self):
        """Setup database configuration"""
        pool_configs = {
            Environment.DEVELOPMENT: (5, 10, 30),
            Environment.TESTING: (2, 5, 20),
            Environment.STAGING: (10, 20, 45),
            Environment.PRODUCTION: (20, 50, 60)
        }
        
        pool_size, max_overflow, pool_timeout = pool_configs.get(
            self.environment, (5, 10, 30)
        )
        
        self.DATABASE_CONFIG = DatabaseConfig(
            url=self.DATABASE_URL,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=pool_timeout,
            enable_logging=self.environment == Environment.DEVELOPMENT
        )

    def _setup_cache_config(self):
        """Setup caching configuration"""
        self.CACHE_CONFIG = {
            "redis_url": self.REDIS_URL,
            "default_timeout": 3600,  # 1 hour
            "key_prefix": f"content_analytics_{self.environment.value}",
            "max_memory_policy": "allkeys-lru",
            "agent_cache_timeouts": {
                "script_analyzer": 7200,      # 2 hours
                "genre_classifier": 3600,     # 1 hour
                "marketing_insights": 1800    # 30 minutes
            }
        }

    def _setup_security_config(self):
        """Setup security configuration"""
        self.SECURITY_CONFIG = {
            "secret_key": self.SECRET_KEY,
            "session_timeout": 3600,
            "max_login_attempts": 5,
            "password_min_length": 8,
            "require_https": self.environment == Environment.PRODUCTION,
            "csrf_protection": True,
            "content_security_policy": {
                "default-src": "'self'",
                "script-src": "'self' 'unsafe-inline'",
                "style-src": "'self' 'unsafe-inline'",
                "img-src": "'self' data: https:"
            }
        }

    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """
        Get configuration for a specific agent
        
        Args:
            agent_name (str): Name of the agent
            
        Returns:
            Optional[AgentConfig]: Agent configuration or None if not found
        """
        return self.AGENT_CONFIGS.get(agent_name)

    def is_agent_enabled(self, agent_name: str) -> bool:
        """
        Check if an agent is enabled
        
        Args:
            agent_name (str): Name of the agent
            
        Returns:
            bool: True if agent is enabled, False otherwise
        """
        config = self.get_agent_config(agent_name)
        return config.enabled if config else False

    def get_cache_timeout(self, agent_name: str) -> int:
        """
        Get cache timeout for a specific agent
        
        Args:
            agent_name (str): Name of the agent
            
        Returns:
            int: Cache timeout in seconds
        """
        return self.CACHE_CONFIG["agent_cache_timeouts"].get(
            agent_name, self.CACHE_CONFIG["default_timeout"]
        )

    def validate_configuration(self) -> List[str]:
        """
        Validate configuration and return any issues
        
        Returns:
            List[str]: List of configuration issues (empty if valid)
        """
        issues = []
        
        # Validate required environment variables
        if not self.SECRET_KEY or self.SECRET_KEY == "dev-secret-key-change-in-production":
            if self.environment == Environment.PRODUCTION:
                issues.append("SECRET_KEY must be set for production environment")
        
        # Validate database URL
        if not self.DATABASE_URL:
            issues.append("DATABASE_URL is required")
        
        # Validate agent configurations
        for agent_name, config in self.AGENT_CONFIGS.items():
            if config.max_processing_time <= 0:
                issues.append(f"Invalid max_processing_time for {agent_name}")
            if config.memory_limit_mb <= 0:
                issues.append(f"Invalid memory_limit_mb for {agent_name}")
        
        # Validate API configuration
        if self.API_CONFIG.port <= 0 or self.API_CONFIG.port > 65535:
            issues.append("Invalid API port number")
        
        if self.API_CONFIG.max_content_length <= 0:
            issues.append("Invalid max_content_length")
        
        return issues

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary format
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            "environment": self.environment.value,
            "api_config": {
                "host": self.API_CONFIG.host,
                "port": self.API_CONFIG.port,
                "debug": self.API_CONFIG.debug,
                "cors_enabled": self.API_CONFIG.cors_enabled
            },
            "agent_configs": {
                name: {
                    "name": config.name,
                    "version": config.version,
                    "enabled": config.enabled,
                    "max_processing_time": config.max_processing_time
                }
                for name, config in self.AGENT_CONFIGS.items()
            },
            "cache_enabled": bool(self.REDIS_URL),
            "analytics_enabled": self.ANALYTICS_ENABLED,
            "log_level": self.LOG_LEVEL.value
        }

# Constants for the application
class Constants:
    """Application-wide constants"""
    
    # API Constants
    API_VERSION = "3.0.0"
    API_TITLE = "Multi-Agent Content Analytics Platform"
    API_DESCRIPTION = """
    Advanced content analysis platform using specialized AI agents for
    script analysis, genre classification, and marketing insights.
    """
    
    # Agent Constants
    SUPPORTED_AGENTS = [
        "script_analyzer",
        "genre_classifier", 
        "marketing_insights"
    ]
    
    # Content Analysis Constants
    MAX_CONTENT_LENGTH = 1048576  # 1MB
    MIN_CONTENT_LENGTH = 10       # 10 characters
    
    # Cache Keys
    CACHE_KEY_TEMPLATES = {
        "agent_result": "agent_result:{agent}:{content_hash}",
        "user_session": "user_session:{session_id}",
        "rate_limit": "rate_limit:{ip_address}"
    }
    
    # Response Codes
    SUCCESS_CODES = {
        "ANALYSIS_COMPLETE": "ANALYSIS_COMPLETE",
        "AGENT_READY": "AGENT_READY",
        "CACHE_HIT": "CACHE_HIT"
    }
    
    ERROR_CODES = {
        "AGENT_NOT_FOUND": "AGENT_NOT_FOUND",
        "AGENT_DISABLED": "AGENT_DISABLED",
        "CONTENT_TOO_LARGE": "CONTENT_TOO_LARGE",
        "CONTENT_TOO_SMALL": "CONTENT_TOO_SMALL",
        "PROCESSING_TIMEOUT": "PROCESSING_TIMEOUT",
        "INVALID_INPUT": "INVALID_INPUT",
        "RATE_LIMIT_EXCEEDED": "RATE_LIMIT_EXCEEDED"
    }
    
    # Default Values
    DEFAULT_AGENT = "script_analyzer"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_CACHE_TIMEOUT = 3600

# Global configuration instance
# This will be initialized based on environment
config: Optional[ContentAnalyticsConfig] = None

def get_config() -> ContentAnalyticsConfig:
    """
    Get the global configuration instance
    
    Returns:
        ContentAnalyticsConfig: Global configuration instance
    """
    global config
    if config is None:
        # Determine environment from environment variable
        env_name = os.getenv("ENVIRONMENT", "development").lower()
        try:
            environment = Environment(env_name)
        except ValueError:
            environment = Environment.DEVELOPMENT
        
        config = ContentAnalyticsConfig(environment)
    
    return config

def setup_logging():
    """Setup logging based on configuration"""
    config = get_config()
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.value),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

def validate_environment():
    """
    Validate the current environment configuration
    
    Raises:
        ValueError: If configuration is invalid
    """
    config = get_config()
    issues = config.validate_configuration()
    
    if issues:
        raise ValueError(f"Configuration validation failed: {'; '.join(issues)}")

# Export commonly used items
__all__ = [
    "ContentAnalyticsConfig",
    "AgentConfig", 
    "APIConfig",
    "DatabaseConfig",
    "Environment",
    "LogLevel",
    "Constants",
    "get_config",
    "setup_logging",
    "validate_environment"
]
