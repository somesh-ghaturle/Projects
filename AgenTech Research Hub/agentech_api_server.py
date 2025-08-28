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
        # Simulate research with realistic processing time
        await asyncio.sleep(0.5)
        
        # Generate realistic research sources based on the query
        query_lower = research_request.query.lower()
        
        # Create relevant sources based on query content
        real_sources = []
        
        # AI/Technology related queries
        if any(term in query_lower for term in ['artificial intelligence', 'ai', 'machine learning', 'ml', 'deep learning', 'neural network']):
            real_sources.extend([
                {
                    "title": "Artificial Intelligence News and Research - MIT Technology Review",
                    "url": "https://www.technologyreview.com/topic/artificial-intelligence/",
                    "snippet": "Latest breakthroughs and developments in artificial intelligence, machine learning, and deep learning technologies.",
                    "relevance_score": 0.95
                },
                {
                    "title": "AI Research Papers - arXiv.org",
                    "url": "https://arxiv.org/list/cs.AI/recent",
                    "snippet": "Recent artificial intelligence research papers and preprints from leading researchers worldwide.",
                    "relevance_score": 0.90
                },
                {
                    "title": "OpenAI Research",
                    "url": "https://openai.com/research/",
                    "snippet": "Cutting-edge research in artificial intelligence, including GPT models, robotics, and safety research.",
                    "relevance_score": 0.88
                }
            ])
        
        # Healthcare related queries
        if any(term in query_lower for term in ['healthcare', 'medical', 'medicine', 'health', 'clinical', 'patient']):
            real_sources.extend([
                {
                    "title": "PubMed - National Center for Biotechnology Information",
                    "url": "https://pubmed.ncbi.nlm.nih.gov/",
                    "snippet": "Comprehensive database of biomedical literature with millions of research articles and clinical studies.",
                    "relevance_score": 0.95
                },
                {
                    "title": "World Health Organization (WHO)",
                    "url": "https://www.who.int/",
                    "snippet": "Global health information, guidelines, and research from the World Health Organization.",
                    "relevance_score": 0.90
                },
                {
                    "title": "Nature Medicine",
                    "url": "https://www.nature.com/nm/",
                    "snippet": "Leading medical research journal covering clinical research, drug discovery, and healthcare innovations.",
                    "relevance_score": 0.87
                }
            ])
        
        # Technology/Programming related queries
        if any(term in query_lower for term in ['programming', 'software', 'development', 'coding', 'python', 'javascript', 'tech']):
            real_sources.extend([
                {
                    "title": "Stack Overflow",
                    "url": "https://stackoverflow.com/",
                    "snippet": "The largest community of developers sharing knowledge and solving programming challenges.",
                    "relevance_score": 0.92
                },
                {
                    "title": "GitHub",
                    "url": "https://github.com/",
                    "snippet": "World's leading software development platform with millions of open source projects and repositories.",
                    "relevance_score": 0.89
                },
                {
                    "title": "TechCrunch",
                    "url": "https://techcrunch.com/",
                    "snippet": "Latest technology news, startup coverage, and innovation in the tech industry.",
                    "relevance_score": 0.85
                }
            ])
        
        # Science/Research related queries
        if any(term in query_lower for term in ['science', 'research', 'study', 'academic', 'scientific']):
            real_sources.extend([
                {
                    "title": "Google Scholar",
                    "url": "https://scholar.google.com/",
                    "snippet": "Comprehensive search for scholarly literature across various disciplines and sources.",
                    "relevance_score": 0.94
                },
                {
                    "title": "Nature",
                    "url": "https://www.nature.com/",
                    "snippet": "Leading international journal of science featuring groundbreaking research across all scientific fields.",
                    "relevance_score": 0.91
                },
                {
                    "title": "Science Magazine - AAAS",
                    "url": "https://www.science.org/",
                    "snippet": "Peer-reviewed research and news from the American Association for the Advancement of Science.",
                    "relevance_score": 0.88
                }
            ])
        
        # Business/Finance related queries
        if any(term in query_lower for term in ['business', 'finance', 'economy', 'market', 'investment', 'startup']):
            real_sources.extend([
                {
                    "title": "Harvard Business Review",
                    "url": "https://hbr.org/",
                    "snippet": "Management insights, business strategy, and leadership advice from Harvard Business School.",
                    "relevance_score": 0.92
                },
                {
                    "title": "Bloomberg",
                    "url": "https://www.bloomberg.com/",
                    "snippet": "Global financial news, market data, and business insights for professionals and investors.",
                    "relevance_score": 0.90
                },
                {
                    "title": "McKinsey & Company Insights",
                    "url": "https://www.mckinsey.com/insights",
                    "snippet": "Strategic insights and analysis on business trends, management, and global economic issues.",
                    "relevance_score": 0.87
                }
            ])
        
        # Education related queries
        if any(term in query_lower for term in ['education', 'learning', 'university', 'course', 'training']):
            real_sources.extend([
                {
                    "title": "Coursera",
                    "url": "https://www.coursera.org/",
                    "snippet": "Online courses and degrees from top universities and companies worldwide.",
                    "relevance_score": 0.91
                },
                {
                    "title": "MIT OpenCourseWare",
                    "url": "https://ocw.mit.edu/",
                    "snippet": "Free online publication of MIT course materials, lectures, and educational resources.",
                    "relevance_score": 0.89
                },
                {
                    "title": "Khan Academy",
                    "url": "https://www.khanacademy.org/",
                    "snippet": "Free online learning platform offering courses in mathematics, science, and humanities.",
                    "relevance_score": 0.86
                }
            ])
        
        # Default general sources if no specific category matches
        if not real_sources:
            real_sources = [
                {
                    "title": "Wikipedia",
                    "url": "https://wikipedia.org/",
                    "snippet": f"Comprehensive encyclopedia entry related to: {research_request.query}",
                    "relevance_score": 0.80
                },
                {
                    "title": "Britannica",
                    "url": "https://www.britannica.com/",
                    "snippet": f"Authoritative reference information about: {research_request.query}",
                    "relevance_score": 0.78
                },
                {
                    "title": "BBC News",
                    "url": "https://www.bbc.com/news",
                    "snippet": f"Latest news and information coverage about: {research_request.query}",
                    "relevance_score": 0.75
                }
            ]
        
        # Limit to top 5 most relevant sources
        selected_sources = sorted(real_sources, key=lambda x: x['relevance_score'], reverse=True)[:5]
        
        # Generate a more intelligent summary
        summary_content = f"Research on '{research_request.query}' reveals several key insights from authoritative sources. "
        
        if any(term in query_lower for term in ['artificial intelligence', 'ai']):
            summary_content += "The field of artificial intelligence continues to evolve rapidly with advances in machine learning, natural language processing, and neural networks. Current research focuses on improving model efficiency, safety, and real-world applications."
        elif any(term in query_lower for term in ['healthcare', 'medical']):
            summary_content += "Healthcare research emphasizes evidence-based medicine, clinical trials, and innovative treatments. Current trends include personalized medicine, digital health technologies, and preventive care approaches."
        elif any(term in query_lower for term in ['technology', 'programming']):
            summary_content += "Technology development continues to accelerate with focus on software engineering best practices, emerging programming paradigms, and innovative solutions to complex technical challenges."
        else:
            summary_content += "The research encompasses multiple perspectives and authoritative sources, providing comprehensive coverage of the topic with emphasis on current developments and established knowledge."
        
        execution_time = time.time() - start_time
        
        logger.info(f"Research completed for: {research_request.query}")
        
        return ResearchResponse(
            success=True,
            query=research_request.query,
            sources_found=len(selected_sources),
            sources=selected_sources,
            summary=summary_content,
            quality_score=round(sum(source['relevance_score'] for source in selected_sources) / len(selected_sources), 2),
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
