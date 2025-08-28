"""
Exception handlers for production API
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


async def handle_validation_error(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    logger.warning(
        f"Validation error on {request.method} {request.url}",
        extra={
            "errors": exc.errors(),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )


async def handle_http_exception(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper logging"""
    logger.warning(
        f"HTTP exception on {request.method} {request.url}: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "Request Error",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        },
        headers=exc.headers
    )


async def handle_general_exception(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(
        f"Unexpected error on {request.method} {request.url}: {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )
