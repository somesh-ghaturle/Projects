#!/usr/bin/env python3
"""
Simple API server for testing
"""

import sys
import os
sys.path.append('src')

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import asyncio

from agents.researcher_agent import ResearcherAgent

app = FastAPI(title="AgenTech Research Hub API", version="1.0.0")

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

# Initialize the research agent
researcher = ResearcherAgent()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AgenTech Research Hub API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "research": "/research",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AgenTech Research Hub"}

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest):
    """Conduct research on a given query"""
    try:
        # Execute research
        result = await researcher.execute(request.query, request.context)
        
        return ResearchResponse(
            success=True,
            query=request.query,
            sources_found=result.get('sources_found', 0),
            sources=result.get('sources', []),
            summary=result.get('summary', ''),
            quality_score=result.get('research_quality', {}).get('quality_score', 0.0)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "system": "AgenTech Research Hub",
        "version": "1.0.0",
        "researcher_agent": "active",
        "capabilities": [
            "dynamic_topic_detection",
            "multi_source_research",
            "real_url_mapping"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
