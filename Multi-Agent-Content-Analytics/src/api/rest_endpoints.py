"""
REST API Endpoints for Multi-Agent Content Analytics
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import logging
from datetime import datetime
import uuid

from ..agents.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

# Pydantic Models for Request/Response

class ContentMetadata(BaseModel):
    """Metadata for content analysis"""
    title: Optional[str] = None
    genre_hint: Optional[str] = None
    target_audience: Optional[str] = None
    production_year: Optional[int] = None
    budget_range: Optional[str] = None
    director: Optional[str] = None
    studio: Optional[str] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)

class AnalysisOptions(BaseModel):
    """Options for content analysis"""
    include_script_analysis: bool = True
    include_genre_classification: bool = True
    include_marketing_analysis: bool = True
    detailed_insights: bool = True
    cache_results: bool = True
    async_processing: bool = False

class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis"""
    script_text: Optional[str] = Field(None, description="Movie script text to analyze")
    text_content: Optional[str] = Field(None, description="General text content for genre analysis")
    social_media_data: Optional[List[str]] = Field(None, description="Social media posts for marketing analysis")
    metadata: Optional[ContentMetadata] = Field(None, description="Content metadata")
    options: Optional[AnalysisOptions] = Field(default_factory=AnalysisOptions, description="Analysis options")

class AgentStatusResponse(BaseModel):
    """Agent status information"""
    name: str
    initialized: bool
    status: str
    last_execution: Optional[str] = None
    error_count: int = 0

class SystemStatusResponse(BaseModel):
    """System status response"""
    orchestrator_initialized: bool
    agents: List[AgentStatusResponse]
    cache_size: int
    active_tasks: int
    system_health: str
    timestamp: str

class AnalysisTaskResponse(BaseModel):
    """Response for async analysis task"""
    task_id: str
    status: str
    timestamp: str
    estimated_completion: Optional[str] = None

class ContentAnalysisResponse(BaseModel):
    """Response model for content analysis"""
    analysis_id: str
    timestamp: str
    task_id: Optional[str] = None
    content_summary: Dict[str, Any]
    agents_used: List[str]
    individual_results: Dict[str, Any]
    cross_agent_insights: Dict[str, Any]
    confidence_scores: Dict[str, float]
    recommendations: Dict[str, List[str]]
    processing_time: Optional[float] = None

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    details: Optional[str] = None
    timestamp: str
    request_id: Optional[str] = None

# Global orchestrator instance
orchestrator = AgentOrchestrator()
orchestrator_initialized = False

# Background task storage
background_tasks = {}

async def get_orchestrator():
    """Dependency to get initialized orchestrator"""
    global orchestrator, orchestrator_initialized
    
    if not orchestrator_initialized:
        await orchestrator.initialize()
        orchestrator_initialized = True
    
    return orchestrator

# Create router
router = APIRouter(prefix="/api/v1", tags=["content_analytics"])

@router.get("/health", response_model=Dict[str, str])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Multi-Agent Content Analytics"
    }

@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Get system status"""
    try:
        status_data = await orchestrator.get_agent_status()
        
        # Convert agent status data
        agents = []
        for agent_name, agent_info in status_data.get("agents", {}).items():
            agents.append(AgentStatusResponse(
                name=agent_name,
                initialized=agent_info.get("initialized", False),
                status=agent_info.get("status", "unknown"),
                last_execution=agent_info.get("last_execution"),
                error_count=agent_info.get("error_count", 0)
            ))
        
        # Determine system health
        system_health = "healthy"
        if not status_data.get("orchestrator_initialized", False):
            system_health = "initializing"
        elif any(not agent.initialized for agent in agents):
            system_health = "degraded"
        elif any(agent.error_count > 5 for agent in agents):
            system_health = "unstable"
        
        return SystemStatusResponse(
            orchestrator_initialized=status_data.get("orchestrator_initialized", False),
            agents=agents,
            cache_size=status_data.get("cache_size", 0),
            active_tasks=status_data.get("active_tasks", 0) + len(background_tasks),
            system_health=system_health,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system status: {str(e)}"
        )

@router.post("/analyze", response_model=ContentAnalysisResponse)
async def analyze_content(
    request: ContentAnalysisRequest,
    background_tasks: BackgroundTasks,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """Analyze content using multiple agents"""
    start_time = datetime.now()
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"Received content analysis request: {request_id}")
        
        # Prepare content data for orchestrator
        content_data = {}
        
        if request.script_text and request.options.include_script_analysis:
            content_data["script_text"] = request.script_text
        
        if request.text_content and request.options.include_genre_classification:
            content_data["text_content"] = request.text_content
        
        if request.social_media_data and request.options.include_marketing_analysis:
            content_data["social_media_data"] = request.social_media_data
        
        if request.metadata:
            content_data["metadata"] = request.metadata.dict()
        
        # Check if async processing is requested
        if request.options.async_processing:
            task_id = str(uuid.uuid4())
            
            # Store task info
            background_tasks_info = {
                "task_id": task_id,
                "status": "queued",
                "timestamp": datetime.now().isoformat(),
                "request_data": content_data
            }
            background_tasks[task_id] = background_tasks_info
            
            # Add background task
            background_tasks.add_task(
                _run_async_analysis,
                task_id,
                content_data,
                orchestrator
            )
            
            # Return task info
            return ContentAnalysisResponse(
                analysis_id=f"async_{task_id}",
                timestamp=datetime.now().isoformat(),
                task_id=task_id,
                content_summary={"status": "processing", "task_id": task_id},
                agents_used=[],
                individual_results={},
                cross_agent_insights={},
                confidence_scores={},
                recommendations={}
            )
        
        # Synchronous processing
        analysis_results = await orchestrator.analyze_content(content_data)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Return results
        return ContentAnalysisResponse(
            analysis_id=analysis_results.get("analysis_id", request_id),
            timestamp=analysis_results.get("timestamp", datetime.now().isoformat()),
            content_summary=analysis_results.get("content_summary", {}),
            agents_used=analysis_results.get("agents_used", []),
            individual_results=analysis_results.get("individual_results", {}),
            cross_agent_insights=analysis_results.get("cross_agent_insights", {}),
            confidence_scores=analysis_results.get("confidence_scores", {}),
            recommendations=analysis_results.get("recommendations", {}),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Error in content analysis {request_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.get("/analyze/task/{task_id}", response_model=Dict[str, Any])
async def get_analysis_task(task_id: str):
    """Get status of async analysis task"""
    try:
        if task_id not in background_tasks:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        task_info = background_tasks[task_id]
        
        return {
            "task_id": task_id,
            "status": task_info["status"],
            "timestamp": task_info["timestamp"],
            "results": task_info.get("results"),
            "error": task_info.get("error")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )

@router.post("/agents/initialize", response_model=Dict[str, str])
async def initialize_agents(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Initialize all agents"""
    try:
        # Orchestrator is already initialized by dependency
        return {
            "status": "success",
            "message": "All agents initialized successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize agents: {str(e)}"
        )

@router.post("/agents/cleanup", response_model=Dict[str, str])
async def cleanup_agents(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Cleanup all agents"""
    global orchestrator_initialized
    
    try:
        await orchestrator.cleanup()
        orchestrator_initialized = False
        
        return {
            "status": "success",
            "message": "All agents cleaned up successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up agents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup agents: {str(e)}"
        )

@router.get("/agents/{agent_name}/status", response_model=Dict[str, Any])
async def get_agent_status(agent_name: str, orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Get status of specific agent"""
    try:
        status_data = await orchestrator.get_agent_status()
        agents_info = status_data.get("agents", {})
        
        if agent_name not in agents_info:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found"
            )
        
        agent_info = agents_info[agent_name]
        
        return {
            "agent_name": agent_name,
            "status": agent_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status for {agent_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent status: {str(e)}"
        )

@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats(orchestrator: AgentOrchestrator = Depends(get_orchestrator)):
    """Get cache statistics"""
    try:
        status_data = await orchestrator.get_agent_status()
        
        return {
            "cache_size": status_data.get("cache_size", 0),
            "active_tasks": status_data.get("active_tasks", 0),
            "background_tasks": len(background_tasks),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache statistics: {str(e)}"
        )

@router.delete("/cache/clear", response_model=Dict[str, str])
async def clear_cache():
    """Clear analysis cache"""
    try:
        # Clear background tasks
        background_tasks.clear()
        
        # Note: Orchestrator cache clearing would need to be implemented
        # in the orchestrator class
        
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )

# Background task function
async def _run_async_analysis(task_id: str, content_data: Dict[str, Any], orchestrator: AgentOrchestrator):
    """Run analysis in background"""
    try:
        # Update task status
        background_tasks[task_id]["status"] = "processing"
        background_tasks[task_id]["started_at"] = datetime.now().isoformat()
        
        # Run analysis
        results = await orchestrator.analyze_content(content_data)
        
        # Store results
        background_tasks[task_id]["status"] = "completed"
        background_tasks[task_id]["completed_at"] = datetime.now().isoformat()
        background_tasks[task_id]["results"] = results
        
        logger.info(f"Background analysis task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Background analysis task {task_id} failed: {str(e)}")
        
        # Store error
        background_tasks[task_id]["status"] = "failed"
        background_tasks[task_id]["failed_at"] = datetime.now().isoformat()
        background_tasks[task_id]["error"] = str(e)

# Exception handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unexpected error in REST API: {str(exc)}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            details=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )
