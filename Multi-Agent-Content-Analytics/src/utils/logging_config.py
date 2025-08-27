"""
Logging configuration for Multi-Agent Content Analytics
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Setup logging configuration for the application
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (default: logs/app.log)
        log_format: Custom log format string
        enable_console: Enable console logging
        enable_file: Enable file logging
        max_file_size: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    """
    
    # Default log format
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )
    
    # Default log file
    if log_file is None:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "app.log"
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed": {
                "format": (
                    "%(asctime)s - %(name)s - %(levelname)s - "
                    "[%(filename)s:%(lineno)d:%(funcName)s] - "
                    "%(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            }
        },
        "handlers": {},
        "loggers": {
            "": {  # Root logger
                "level": log_level,
                "handlers": [],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": [],
                "propagate": False
            },
            "fastapi": {
                "level": "INFO",
                "handlers": [],
                "propagate": False
            }
        }
    }
    
    # Console handler
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        }
        config["loggers"][""]["handlers"].append("console")
        config["loggers"]["uvicorn"]["handlers"].append("console")
        config["loggers"]["fastapi"]["handlers"].append("console")
    
    # File handler with rotation
    if enable_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "detailed",
            "filename": str(log_file),
            "maxBytes": max_file_size,
            "backupCount": backup_count,
            "encoding": "utf-8"
        }
        config["loggers"][""]["handlers"].append("file")
        config["loggers"]["uvicorn"]["handlers"].append("file")
        config["loggers"]["fastapi"]["handlers"].append("file")
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    logger.info(f"Log level: {log_level}")
    if enable_file:
        logger.info(f"Log file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """Get logger instance with specified name"""
    return logging.getLogger(name)

def set_log_level(level: str) -> None:
    """Set log level for root logger"""
    logging.getLogger().setLevel(getattr(logging, level.upper()))

class StructuredLogger:
    """Structured logger for consistent log formatting"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """Log with structured data"""
        extra_data = {
            "timestamp": datetime.now().isoformat(),
            "logger_name": self.name,
            **kwargs
        }
        
        # Format message with extra data if provided
        if kwargs:
            formatted_kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} | {formatted_kwargs}"
        
        getattr(self.logger, level.lower())(message, extra=extra_data)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self._log("DEBUG", message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        self._log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message"""
        self._log("CRITICAL", message, **kwargs)
    
    def agent_activity(self, agent_name: str, activity: str, **kwargs) -> None:
        """Log agent activity"""
        self.info(
            f"Agent activity: {activity}",
            agent_name=agent_name,
            activity=activity,
            **kwargs
        )
    
    def api_request(self, method: str, endpoint: str, status_code: int = None, **kwargs) -> None:
        """Log API request"""
        self.info(
            f"API {method} {endpoint}",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            **kwargs
        )
    
    def analysis_start(self, analysis_id: str, content_type: str, **kwargs) -> None:
        """Log analysis start"""
        self.info(
            f"Analysis started: {analysis_id}",
            analysis_id=analysis_id,
            content_type=content_type,
            event_type="analysis_start",
            **kwargs
        )
    
    def analysis_complete(self, analysis_id: str, processing_time: float, **kwargs) -> None:
        """Log analysis completion"""
        self.info(
            f"Analysis completed: {analysis_id}",
            analysis_id=analysis_id,
            processing_time=processing_time,
            event_type="analysis_complete",
            **kwargs
        )
    
    def model_training(self, model_name: str, event: str, **kwargs) -> None:
        """Log model training events"""
        self.info(
            f"Model {event}: {model_name}",
            model_name=model_name,
            event_type=f"model_{event}",
            **kwargs
        )

class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, name: str):
        self.logger = StructuredLogger(f"{name}.performance")
    
    def log_execution_time(
        self,
        operation: str,
        execution_time: float,
        success: bool = True,
        **kwargs
    ) -> None:
        """Log operation execution time"""
        self.logger.info(
            f"Operation: {operation}",
            operation=operation,
            execution_time=execution_time,
            success=success,
            metric_type="execution_time",
            **kwargs
        )
    
    def log_memory_usage(
        self,
        operation: str,
        memory_mb: float,
        **kwargs
    ) -> None:
        """Log memory usage"""
        self.logger.info(
            f"Memory usage: {operation}",
            operation=operation,
            memory_mb=memory_mb,
            metric_type="memory_usage",
            **kwargs
        )
    
    def log_throughput(
        self,
        operation: str,
        items_processed: int,
        time_taken: float,
        **kwargs
    ) -> None:
        """Log throughput metrics"""
        throughput = items_processed / time_taken if time_taken > 0 else 0
        
        self.logger.info(
            f"Throughput: {operation}",
            operation=operation,
            items_processed=items_processed,
            time_taken=time_taken,
            throughput=throughput,
            metric_type="throughput",
            **kwargs
        )

class AuditLogger:
    """Logger for audit events"""
    
    def __init__(self, name: str):
        self.logger = StructuredLogger(f"{name}.audit")
    
    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        success: bool = True,
        **kwargs
    ) -> None:
        """Log data access events"""
        self.logger.info(
            f"Data access: {action} {resource}",
            user_id=user_id,
            resource=resource,
            action=action,
            success=success,
            event_type="data_access",
            **kwargs
        )
    
    def log_model_update(
        self,
        model_name: str,
        action: str,
        user_id: str = None,
        **kwargs
    ) -> None:
        """Log model update events"""
        self.logger.info(
            f"Model update: {action} {model_name}",
            model_name=model_name,
            action=action,
            user_id=user_id,
            event_type="model_update",
            **kwargs
        )
    
    def log_system_event(
        self,
        event: str,
        severity: str = "INFO",
        **kwargs
    ) -> None:
        """Log system events"""
        log_func = getattr(self.logger, severity.lower(), self.logger.info)
        log_func(
            f"System event: {event}",
            event=event,
            severity=severity,
            event_type="system_event",
            **kwargs
        )

# Predefined logger instances
app_logger = StructuredLogger("app")
agent_logger = StructuredLogger("agents")
api_logger = StructuredLogger("api")
ml_logger = StructuredLogger("ml")
data_logger = StructuredLogger("data")

performance_logger = PerformanceLogger("app")
audit_logger = AuditLogger("app")

# Export commonly used loggers
__all__ = [
    "setup_logging",
    "get_logger",
    "set_log_level",
    "StructuredLogger",
    "PerformanceLogger",
    "AuditLogger",
    "app_logger",
    "agent_logger",
    "api_logger",
    "ml_logger",
    "data_logger",
    "performance_logger",
    "audit_logger"
]
