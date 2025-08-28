#!/usr/bin/env python3
"""
Simplified API server for testing and development
"""

import sys
import os
import logging
import signal
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

# Add src to path
sys.path.append('src')

from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ValidationError
from fastapi.responses import JSONResponse
import uvicorn

from src.config.settings import get_settings
from src.core.monitoring import setup_monitoring, health_checker
from src.core.security import verify_api_key
from src.core.exceptions import handle_validation_error, handle_http_exception

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    logger.info("Starting AgenTech Research Hub API")
    
    # Startup
    await setup_monitoring()
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
    lifespan=lifespan
)

# Add middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(ValidationError, handle_validation_error)
app.add_exception_handler(HTTPException, handle_http_exception)

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
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

# API Key dependency (optional for development)
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
            "status": "/status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
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
async def conduct_research(
    request: Request,
    research_request: ResearchRequest,
    _: bool = Depends(get_api_key)
):
    """Conduct research on a given query (simplified for testing)"""
    start_time = time.time()
    
    logger.info(f"Research request: {research_request.query}")
    
    try:
        # Simulate research (replace with actual research agent)
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Mock research results
        mock_sources = [
            {
                "title": f"Research result for: {research_request.query}",
                "url": "https://example.com/research",
                "snippet": f"This is a mock research result for the query: {research_request.query}",
                "relevance_score": 0.85
            }
        ]
        
        mock_summary = f"Based on the research query '{research_request.query}', this is a summarized response. In a production environment, this would contain actual research results from multiple sources including academic papers, web searches, and news articles."
        
        execution_time = time.time() - start_time
        
        logger.info(f"Research completed for: {research_request.query}")
        
        return ResearchResponse(
            success=True,
            query=research_request.query,
            sources_found=len(mock_sources),
            sources=mock_sources,
            summary=mock_summary,
            quality_score=0.85,
            execution_time=round(execution_time, 2)
        )
    
    except asyncio.TimeoutError:
        logger.error(f"Research timeout for: {research_request.query}")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Research request timed out"
        )
    
    except Exception as e:
        logger.error(f"Research failed for {research_request.query}: {str(e)}")
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
        "researcher_agent": "mock_active",
        "capabilities": [
            "mock_topic_detection",
            "mock_multi_source_research",
            "simplified_api"
        ],
        "features": {
            "web_scraping": settings.enable_web_scraping,
            "academic_search": settings.enable_academic_search,
            "news_search": settings.enable_news_search,
            "api_auth": settings.enable_api_key_auth
        }
    }

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    logger.info(f"🚀 Starting AgenTech Research Hub API Server")
    logger.info(f"📍 Environment: {settings.app_environment}")
    logger.info(f"📍 Server will be available at: http://{settings.api_host}:{settings.api_port}")
    logger.info(f"📖 API Documentation: http://{settings.api_host}:{settings.api_port}/docs")
    logger.info(f"❤️ Health Check: http://{settings.api_host}:{settings.api_port}/health")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
        access_log=True
    )
