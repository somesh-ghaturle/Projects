#!/usr/bin/env python3
"""
Production-ready API server with enhanced security, monitoring, and error handling
"""

import sys
import os
import logging
import signal
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

# Add src to path
sys.path.append('src')

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator
import time
import structlog

from config.settings import get_settings
from agents.researcher_agent import ResearcherAgent
from core.monitoring import setup_monitoring, health_checker
from core.security import verify_api_key
from core.exceptions import handle_validation_error, handle_http_exception

# Setup structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global settings
settings = get_settings()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    logger.info("Starting AgenTech Research Hub API", version=settings.app_version)
    
    # Startup
    await setup_monitoring()
    
    # Initialize components
    app.state.researcher = ResearcherAgent()
    app.state.start_time = time.time()
    
    logger.info("Application startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AgenTech Research Hub API")

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.app_description,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add middleware
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware with production settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Trusted host middleware for production
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Exception handlers
app.add_exception_handler(ValidationError, handle_validation_error)
app.add_exception_handler(HTTPException, handle_http_exception)

# Prometheus metrics
if settings.enable_metrics:
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app)

# Request models
class ResearchRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}

class ResearchResponse(BaseModel):
    success: bool
    query: str
    sources_found: int
    sources: list
    summary: str
    quality_score: float
    execution_time: float

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request received",
        method=request.method,
        url=str(request.url),
        client_ip=get_remote_address(request)
    )
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        process_time=round(process_time, 4)
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# API Key dependency
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if settings.enable_api_key_auth:
        return verify_api_key(api_key)
    return True

# Routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "environment": settings.app_environment,
        "endpoints": {
            "health": "/health",
            "research": "/research",
            "metrics": "/metrics" if settings.enable_metrics else "disabled"
        }
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    uptime = time.time() - app.state.start_time
    
    health_status = await health_checker.check_all_services()
    
    return {
        "status": "healthy" if health_status["overall"] else "unhealthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "uptime": round(uptime, 2),
        "environment": settings.app_environment,
        "checks": health_status["services"]
    }

@app.post("/research", response_model=ResearchResponse)
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def conduct_research(
    request: Request,
    research_request: ResearchRequest,
    _: bool = Depends(get_api_key)
):
    """Conduct research on a given query with rate limiting and authentication"""
    start_time = time.time()
    
    logger.info(
        "Research request initiated",
        query=research_request.query,
        client_ip=get_remote_address(request)
    )
    
    try:
        # Execute research with timeout
        result = await asyncio.wait_for(
            app.state.researcher.execute(research_request.query, research_request.context),
            timeout=settings.research_timeout_seconds
        )
        
        execution_time = time.time() - start_time
        
        logger.info(
            "Research completed successfully",
            query=research_request.query,
            sources_found=result.get('sources_found', 0),
            execution_time=round(execution_time, 2)
        )
        
        return ResearchResponse(
            success=True,
            query=research_request.query,
            sources_found=result.get('sources_found', 0),
            sources=result.get('sources', []),
            summary=result.get('summary', ''),
            quality_score=result.get('research_quality', {}).get('quality_score', 0.0),
            execution_time=round(execution_time, 2)
        )
    
    except asyncio.TimeoutError:
        logger.error(
            "Research timeout",
            query=research_request.query,
            timeout=settings.research_timeout_seconds
        )
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Research request timed out"
        )
    
    except Exception as e:
        logger.error(
            "Research failed",
            query=research_request.query,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Research failed: {str(e)}"
        )

@app.get("/status")
async def get_status():
    """Get system status and capabilities"""
    return {
        "system": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_environment,
        "researcher_agent": "active",
        "capabilities": [
            "dynamic_topic_detection",
            "multi_source_research",
            "real_url_mapping",
            "rate_limiting",
            "authentication"
        ],
        "features": {
            "web_scraping": settings.enable_web_scraping,
            "academic_search": settings.enable_academic_search,
            "news_search": settings.enable_news_search,
            "crew_ai": settings.enable_crew_ai,
            "langgraph": settings.enable_langgraph
        }
    }

@app.get("/metrics-summary")
async def get_metrics_summary(_: bool = Depends(get_api_key)):
    """Get application metrics summary"""
    uptime = time.time() - app.state.start_time
    
    return {
        "uptime": round(uptime, 2),
        "environment": settings.app_environment,
        "version": settings.app_version,
        "rate_limit": f"{settings.rate_limit_per_minute}/minute",
        "max_concurrent_agents": settings.max_concurrent_agents,
        "research_timeout": settings.research_timeout_seconds
    }

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # Configure logging level
    log_level = getattr(logging, settings.log_level.upper())
    logging.basicConfig(level=log_level)
    
    logger.info(
        "🚀 Starting AgenTech Research Hub API Server",
        environment=settings.app_environment,
        version=settings.app_version
    )
    logger.info(f"📍 Server will be available at: http://{settings.api_host}:{settings.api_port}")
    
    if settings.debug:
        logger.info(f"📖 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    
    logger.info(f"❤️ Health Check: http://{settings.api_host}:{settings.api_port}/health")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        access_log=True,
        workers=1 if settings.debug else settings.max_workers
    )
