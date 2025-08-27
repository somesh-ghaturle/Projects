"""
API Router Configuration for Multi-Agent Content Analytics
"""

from fastapi import APIRouter
from .rest_endpoints import router as rest_router

# Create main API router
api_router = APIRouter()

# Include REST endpoints
api_router.include_router(rest_router)

# Health check at root level
@api_router.get("/health")
async def health_check():
    """Root health check"""
    return {
        "status": "healthy",
        "service": "Multi-Agent Content Analytics API",
        "version": "1.0.0"
    }
