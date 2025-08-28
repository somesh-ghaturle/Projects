"""
Multi-Agent Content Analytics Platform v3.0.0

Professional-grade FastAPI application for AI-powered content analysis.
Features modular architecture with specialized agents for screenplay analysis,
genre classification, and marketing insights.

Created by: AI Assistant
Version: 3.0.0
License: MIT
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

# Import our modular components
from app.core.config import ContentAnalyticsConfig
from app.models.data_models import (
    AnalysisRequest, 
    AnalysisResponse, 
    BulkAnalysisRequest,
    BulkAnalysisResponse,
    HealthResponse,
    AgentType,
    ContentType,
    PriorityLevel
)
from app.agents.script_analyzer_agent import ScriptAnalyzerAgent
from app.agents.genre_classification_agent import GenreClassificationAgent
from app.agents.marketing_insights_agent import MarketingInsightsAgent
from app.utils.cache_manager import CacheManager
from app.utils import TextProcessor

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global instances
config = ContentAnalyticsConfig()
cache_manager: Optional[CacheManager] = None
text_processor: Optional[TextProcessor] = None
agents: Dict[str, Any] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    global cache_manager, text_processor, agents
    
    # Startup
    logger.info("🚀 Starting Multi-Agent Content Analytics Platform v3.0.0")
    
    try:
        # Initialize cache manager with correct parameter names
        cache_manager = CacheManager(
            memory_cache_size=1000,  # Memory cache size
            default_ttl=3600         # Default TTL of 1 hour
        )
        logger.info("✅ Cache manager initialized")
        
        # Initialize text processor
        text_processor = TextProcessor()
        logger.info("✅ Text processor initialized")
        
        # Initialize agents with default configurations
        agents = {
            "script_analyzer": ScriptAnalyzerAgent(),
            "genre_classifier": GenreClassificationAgent(),
            "marketing_insights": MarketingInsightsAgent()
        }
        logger.info("✅ All agents initialized")
        
        logger.info("🎬 Platform ready for content analysis")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down platform...")
    
    try:
        # Clean up cache
        if cache_manager:
            cache_manager.cleanup()
            logger.info("✅ Cache cleaned up")
        
        # Clean up agents
        for agent_name, agent in agents.items():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()
        logger.info("✅ Agents cleaned up")
        
        logger.info("👋 Platform shutdown complete")
        
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Multi-Agent Content Analytics Platform",
        description="Professional-grade AI-powered content analysis with specialized agents",
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        contact={
            "name": "Content Analytics Team",
            "email": "support@contentalytics.ai"
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Mount static files
    try:
        # Calculate absolute paths to static directories
        base_dir = os.path.dirname(os.path.dirname(__file__))
        static_dir = os.path.join(base_dir, "static")
        frontend_dir = os.path.join(base_dir, "frontend")
        
        if os.path.exists(static_dir):
            app.mount("/static", StaticFiles(directory=static_dir), name="static")
            logger.info(f"✅ Static files mounted from {static_dir}")
        
        if os.path.exists(frontend_dir):
            app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")
            logger.info(f"✅ Frontend files mounted from {frontend_dir}")
        else:
            logger.warning(f"⚠️ Frontend directory not found: {frontend_dir}")
            
    except Exception as e:
        logger.warning(f"⚠️ Failed to mount static files: {e}")
    
    return app


# Create the app instance
app = create_app()


# Dependency injection
async def get_cache_manager() -> CacheManager:
    """Get the cache manager instance."""
    if cache_manager is None:
        raise HTTPException(status_code=500, detail="Cache manager not initialized")
    return cache_manager


async def get_text_processor() -> TextProcessor:
    """Get the text processor instance."""
    if text_processor is None:
        raise HTTPException(status_code=500, detail="Text processor not initialized")
    return text_processor


async def get_agent(agent_type: str):
    """Get a specific agent instance."""
    if agent_type not in agents:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown agent type: {agent_type}. Available: {list(agents.keys())}"
        )
    return agents[agent_type]


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with platform information."""
    return {
        "name": "Multi-Agent Content Analytics Platform",
        "version": "3.0.0",
        "status": "operational",
        "description": "Professional-grade AI-powered content analysis",
        "agents": list(agents.keys()),
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "bulk_analyze": "/bulk_analyze",
            "cache_stats": "/cache/stats",
            "docs": "/docs"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with system status."""
    cache_stats = cache_manager.get_comprehensive_stats()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "cache_stats": cache_stats,
        "services": {
            "content_analyzer": "running",
            "sentiment_analyzer": "running", 
            "comment_generator": "running"
        }
    }


@app.get("/frontend")
async def serve_frontend():
    """Serve the main frontend interface."""
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    index_path = os.path.join(frontend_dir, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")


@app.get("/web")
async def serve_web_interface():
    """Alternative route to serve the web interface."""
    return await serve_frontend()


@app.get("/ui")
async def serve_ui():
    """Another alternative route to serve the UI."""
    return await serve_frontend()


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_content(
    request: AnalysisRequest,
    cache: CacheManager = Depends(get_cache_manager),
    text_proc: TextProcessor = Depends(get_text_processor)
):
    """Analyze content with the specified agent."""
    start_time = time.time()
    
    try:
        logger.info(f"📥 Analysis request: agent={request.agent}, content_length={len(request.content)}")
        
        # Validate content size
        if len(request.content) > config.API_CONFIG.max_content_length:
            raise HTTPException(
                status_code=413,
                detail=f"Content too large. Max size: {config.API_CONFIG.max_content_length} bytes"
            )
        
        # Generate cache key
        cache_key = None
        if request.cache_enabled:
            cache_key = cache.generate_key(request.agent.value, request.content)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"🎯 Cache hit for key: {cache_key[:16]}...")
                return AnalysisResponse(
                    success=True,
                    result=cached_result,
                    agent=request.agent.value,
                    processing_time=time.time() - start_time,
                    cached=True,
                    timestamp=datetime.utcnow().isoformat()
                )
        
        # Get the appropriate agent
        agent = await get_agent(request.agent.value)
        
        # Preprocess content if needed
        processed_content = request.content
        if request.preprocessing_enabled:
            processed_content = text_proc.preprocess_text(request.content)
            logger.info("🔄 Content preprocessed")
        
        # Perform analysis
        logger.info(f"🤖 Running {request.agent.value} analysis...")
        result = agent.analyze(
            content=processed_content,
            parameters=None
        )
        
        # Cache the result
        if cache_key and request.cache_enabled:
            cache.set(cache_key, result)
            logger.info(f"💾 Result cached with key: {cache_key[:16]}...")
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Analysis completed in {processing_time:.2f}s")
        
        return AnalysisResponse(
            success=True,
            result=result,
            agent=request.agent.value,
            processing_time=processing_time,
            cached=False,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except ValidationError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/bulk_analyze", response_model=BulkAnalysisResponse)
async def bulk_analyze(
    request: BulkAnalysisRequest,
    background_tasks: BackgroundTasks,
    cache: CacheManager = Depends(get_cache_manager)
):
    """Perform bulk analysis on multiple content items."""
    start_time = time.time()
    
    try:
        logger.info(f"📦 Bulk analysis request: {len(request.items)} items")
        
        # Validate bulk size
        if len(request.items) > config.max_bulk_size:
            raise HTTPException(
                status_code=413,
                detail=f"Too many items. Max bulk size: {config.max_bulk_size}"
            )
        
        # Process items in parallel
        tasks = []
        for item in request.items:
            # Create individual analysis request
            analysis_req = AnalysisRequest(
                content=item.content,
                agent=item.agent,
                content_type=item.content_type,
                priority=PriorityLevel.LOW  # Bulk requests get lower priority
            )
            tasks.append(analyze_single_item(analysis_req, cache))
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_results.append({
                    "index": i,
                    "error": str(result),
                    "content_preview": request.items[i].content[:100] + "..."
                })
            else:
                successful_results.append(result)
        
        processing_time = time.time() - start_time
        logger.info(f"📊 Bulk analysis completed: {len(successful_results)} success, {len(failed_results)} failed")
        
        return BulkAnalysisResponse(
            success=len(failed_results) == 0,
            results=successful_results,
            failed_items=failed_results,
            total_items=len(request.items),
            successful_items=len(successful_results),
            processing_time=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Bulk analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")


async def analyze_single_item(request: AnalysisRequest, cache: CacheManager) -> Dict[str, Any]:
    """Analyze a single item (helper for bulk analysis)."""
    agent = await get_agent(request.agent.value)
    
    # Check cache
    cache_key = cache.generate_key(request.agent.value, request.content)
    cached_result = cache.get(cache_key)
    
    if cached_result:
        return {
            "agent": request.agent.value,
            "result": cached_result,
            "cached": True
        }
    
    # Perform analysis
    result = agent.analyze(
        content=request.content,
        parameters=None
    )
    
    # Cache result
    cache.set(cache_key, result)
    
    return {
        "agent": request.agent.value,
        "result": result,
        "cached": False
    }


@app.get("/cache/stats", response_model=Dict[str, Any])
async def cache_statistics(cache: CacheManager = Depends(get_cache_manager)):
    """Get cache statistics."""
    try:
        stats = cache.get_comprehensive_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")


@app.delete("/cache/clear")
async def clear_cache(cache: CacheManager = Depends(get_cache_manager)):
    """Clear all cached data."""
    try:
        cache.clear_all()
        logger.info("🗑️ Cache cleared successfully")
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@app.get("/agents", response_model=Dict[str, Any])
async def list_agents():
    """List all available agents and their capabilities."""
    agent_info = {}
    
    for name, agent in agents.items():
        agent_info[name] = {
            "name": getattr(agent, 'name', name),
            "description": getattr(agent, 'description', 'No description available'),
            "capabilities": getattr(agent, 'capabilities', []),
            "supported_content_types": getattr(agent, 'supported_content_types', []),
            "version": getattr(agent, 'version', '1.0.0')
        }
    
    return {
        "agents": agent_info,
        "total_agents": len(agents),
        "timestamp": datetime.utcnow().isoformat()
    }


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with proper logging."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting Multi-Agent Content Analytics Platform...")
    
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG_MODE,
        workers=1,  # Use single worker for development
        log_level="info",
        access_log=True
    )
