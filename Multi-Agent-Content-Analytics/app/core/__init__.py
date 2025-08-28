"""
Core Package - Multi-Agent Content Analytics Platform

This package contains core functionality including configuration management,
base classes, and system utilities.

Author: Content Analytics Team  
Version: 3.0.0
Last Updated: August 2025
"""

from .config import ContentAnalyticsConfig

__version__ = "3.0.0"
__author__ = "Content Analytics Team"
__all__ = ["ContentAnalyticsConfig"]

# Simple exports for backwards compatibility
def get_platform_config():
    """Get the platform configuration instance."""
    return ContentAnalyticsConfig()

def initialize_core_system():
    """Initialize the core system."""
    return {"status": "initialized", "version": __version__}

def get_system_info():
    """Get basic system information."""
    return {
        "platform": "Multi-Agent Content Analytics",
        "version": __version__, 
        "author": __author__
    }

def health_check():
    """Basic health check."""
    return {"status": "healthy", "version": __version__}

from .config import (
    ContentAnalyticsConfig
)

__version__ = "3.0.0"
__author__ = "Content Analytics Team"

# Core system registry
CORE_REGISTRY = {
    "config": ContentAnalyticsConfig
}

# Global configuration instance
_config_instance = None

def get_platform_config() -> ContentAnalyticsConfig:
    """
    Get global platform configuration instance.
    
    Returns:
        ContentAnalyticsConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = get_config()
    return _config_instance

def reload_configuration() -> ContentAnalyticsConfig:
    """
    Reload configuration from environment.
    
    Returns:
        New configuration instance
    """
    global _config_instance
    _config_instance = None
    return get_platform_config()

def initialize_core_system(config_overrides: dict = None) -> dict:
    """
    Initialize core system components.
    
    Args:
        config_overrides: Configuration overrides
    
    Returns:
        Dictionary with initialization status
    """
    status = {}
    
    try:
        # Get configuration
        config = get_platform_config()
        
        # Apply overrides if provided
        if config_overrides:
            for key, value in config_overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Validate environment
        env_status = validate_environment()
        status['environment_validation'] = env_status
        
        # Initialize logging
        import logging
        logging.basicConfig(
            level=getattr(logging, config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        status['logging_initialized'] = True
        
        status['initialization_complete'] = True
        status['config_loaded'] = True
        
    except Exception as e:
        status['error'] = str(e)
        status['initialization_complete'] = False
    
    return status

def get_system_info() -> dict:
    """
    Get comprehensive system information.
    
    Returns:
        Dictionary with system information
    """
    import platform
    import sys
    from datetime import datetime
    
    config = get_platform_config()
    
    return {
        'platform': {
            'system': platform.system(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation()
        },
        'application': {
            'name': 'Multi-Agent Content Analytics Platform',
            'version': __version__,
            'environment': config.environment,
            'debug_mode': config.debug,
            'startup_time': datetime.utcnow().isoformat()
        },
        'configuration': {
            'api_host': config.api_host,
            'api_port': config.api_port,
            'log_level': config.log_level,
            'cache_enabled': config.cache_enabled,
            'agent_timeout': config.agent_timeout
        },
        'system_paths': {
            'python_executable': sys.executable,
            'current_working_directory': config.data_dir,
            'cache_directory': config.cache_dir,
            'log_directory': config.log_dir
        }
    }

def health_check() -> dict:
    """
    Perform system health check.
    
    Returns:
        Dictionary with health status
    """
    import os
    from pathlib import Path
    
    health_status = {
        'overall_status': 'healthy',
        'checks': {},
        'timestamp': None
    }
    
    try:
        from datetime import datetime
        health_status['timestamp'] = datetime.utcnow().isoformat()
        
        config = get_platform_config()
        
        # Check configuration
        health_status['checks']['configuration'] = {
            'status': 'ok',
            'loaded': True,
            'environment': config.environment
        }
        
        # Check directories
        directories = [
            ('data_dir', config.data_dir),
            ('cache_dir', config.cache_dir),
            ('log_dir', config.log_dir)
        ]
        
        dir_status = {}
        for name, path in directories:
            path_obj = Path(path)
            dir_status[name] = {
                'path': str(path),
                'exists': path_obj.exists(),
                'writable': os.access(path, os.W_OK) if path_obj.exists() else False
            }
        
        health_status['checks']['directories'] = dir_status
        
        # Check memory usage (basic)
        import psutil
        memory = psutil.virtual_memory()
        health_status['checks']['memory'] = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_percent': memory.percent,
            'status': 'ok' if memory.percent < 90 else 'warning'
        }
        
        # Check disk space
        disk = psutil.disk_usage('/')
        health_status['checks']['disk'] = {
            'total_gb': round(disk.total / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'used_percent': round((disk.used / disk.total) * 100, 1),
            'status': 'ok' if disk.free > 1024**3 else 'warning'  # 1GB minimum
        }
        
    except ImportError:
        health_status['checks']['system_metrics'] = {
            'status': 'unavailable',
            'reason': 'psutil not installed'
        }
    except Exception as e:
        health_status['overall_status'] = 'error'
        health_status['error'] = str(e)
    
    # Determine overall status
    warning_checks = []
    error_checks = []
    
    for check_name, check_data in health_status['checks'].items():
        if isinstance(check_data, dict):
            if check_data.get('status') == 'warning':
                warning_checks.append(check_name)
            elif check_data.get('status') == 'error':
                error_checks.append(check_name)
    
    if error_checks:
        health_status['overall_status'] = 'error'
    elif warning_checks:
        health_status['overall_status'] = 'warning'
    
    return health_status

__all__ = [
    # Configuration
    "ContentAnalyticsConfig", "get_config", "configure_platform", "validate_environment",
    
    # Core Functions
    "get_platform_config", "reload_configuration", "initialize_core_system",
    "get_system_info", "health_check",
    
    # Registry
    "CORE_REGISTRY"
]
