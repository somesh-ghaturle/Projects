#!/usr/bin/env python3
"""
FastAPI Server for Agentic Finance Workflow
Provides REST API and GraphQL endpoints for testing
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import pandas as pd

# Import our agents
from agents import AgentContext, AgentType
from agents.cleaner import DataCleanerAgent, CleaningRules
from agents.orchestrator import OrchestratorAgent, WorkflowDefinition, WorkflowStep

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Finance Workflow API",
    description="Production-ready financial data processing API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class FinancialDataPoint(BaseModel):
    timestamp: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class CleaningRulesModel(BaseModel):
    handle_missing: str = "interpolate"
    missing_threshold: float = 0.1
    outlier_method: str = "iqr"
    outlier_threshold: float = 3.0
    remove_duplicates: bool = True
    validate_business_hours: bool = True
    validate_price_ranges: bool = True
    min_price: float = 0.01
    max_price_change: float = 0.5

class DataCleaningRequest(BaseModel):
    data: List[FinancialDataPoint]
    cleaning_rules: Optional[CleaningRulesModel] = None

class WorkflowStepModel(BaseModel):
    step_id: str
    agent_type: str
    agent_config: Dict[str, Any] = {}

class WorkflowDefinitionModel(BaseModel):
    workflow_id: str
    name: str
    description: str = ""
    steps: List[WorkflowStepModel]

class WorkflowExecutionRequest(BaseModel):
    workflow_definition: WorkflowDefinitionModel
    input_parameters: Dict[str, Any]
    execution_config: Dict[str, Any] = {}

# Global state for demo
workflow_executions = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Finance Workflow API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "agentic-finance-workflow"
    }

@app.post("/api/v1/clean")
async def clean_data(request: DataCleaningRequest):
    """Clean financial data using DataCleanerAgent"""
    try:
        # Convert request data to DataFrame
        data_dict = [item.dict() for item in request.data]
        df = pd.DataFrame(data_dict)
        
        # Create cleaning rules
        if request.cleaning_rules:
            rules = CleaningRules(
                handle_missing=request.cleaning_rules.handle_missing,
                missing_threshold=request.cleaning_rules.missing_threshold,
                outlier_method=request.cleaning_rules.outlier_method,
                outlier_threshold=request.cleaning_rules.outlier_threshold,
                remove_duplicates=request.cleaning_rules.remove_duplicates,
                validate_business_hours=request.cleaning_rules.validate_business_hours,
                validate_price_ranges=request.cleaning_rules.validate_price_ranges,
                min_price=request.cleaning_rules.min_price,
                max_price_change=request.cleaning_rules.max_price_change
            )
        else:
            rules = CleaningRules()
        
        # Create and execute cleaner agent
        cleaner = DataCleanerAgent(cleaning_rules=rules)
        context = AgentContext(
            agent_id="api_cleaner",
            workflow_id=f"api_clean_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        result = await cleaner.execute({"data": df}, context)
        
        if result.success:
            cleaned_df = result.data['cleaned_data']
            cleaned_data = cleaned_df.to_dict('records')
            
            return {
                "success": True,
                "original_count": len(df),
                "cleaned_count": len(cleaned_df),
                "removed_count": len(df) - len(cleaned_df),
                "quality_score": result.data.get('quality_score'),
                "cleaned_data": cleaned_data,
                "execution_time": result.metadata.get("execution_time"),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.error_message)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/workflow/execute")
async def execute_workflow(request: WorkflowExecutionRequest):
    """Execute a workflow using OrchestratorAgent"""
    try:
        # Convert workflow definition
        workflow_steps = []
        for step_model in request.workflow_definition.steps:
            # Map string agent type to enum
            agent_type_map = {
                "CLEANER": AgentType.CLEANER,
                "cleaner": AgentType.CLEANER
            }
            
            agent_type = agent_type_map.get(step_model.agent_type.upper())
            if not agent_type:
                raise HTTPException(status_code=400, detail=f"Unknown agent type: {step_model.agent_type}")
            
            workflow_step = WorkflowStep(
                step_id=step_model.step_id,
                agent_type=agent_type,
                agent_config=step_model.agent_config
            )
            workflow_steps.append(workflow_step)
        
        workflow_def = WorkflowDefinition(
            workflow_id=request.workflow_definition.workflow_id,
            name=request.workflow_definition.name,
            description=request.workflow_definition.description,
            steps=workflow_steps
        )
        
        # Create and execute orchestrator
        orchestrator = OrchestratorAgent()
        context = AgentContext(
            agent_id="api_orchestrator",
            workflow_id=request.workflow_definition.workflow_id
        )
        
        workflow_input = {
            "workflow_definition": workflow_def,
            "input_parameters": request.input_parameters,
            "execution_config": request.execution_config
        }
        
        result = await orchestrator.execute(workflow_input, context)
        
        if result.success:
            workflow_result = result.data
            execution_id = workflow_result.get('execution_id')
            
            # Store execution for later retrieval
            workflow_executions[execution_id] = {
                "result": workflow_result,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "execution_id": execution_id,
                "status": workflow_result.get('status'),
                "duration": workflow_result.get('duration'),
                "results": workflow_result.get('results'),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=result.error_message)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/workflow/{execution_id}")
async def get_workflow_execution(execution_id: str):
    """Get workflow execution results"""
    if execution_id in workflow_executions:
        return workflow_executions[execution_id]
    else:
        raise HTTPException(status_code=404, detail="Workflow execution not found")

@app.get("/api/v1/stream/status")
async def stream_status():
    """Streaming endpoint status"""
    return {
        "streaming_available": True,
        "active_connections": 0,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get API performance metrics"""
    return {
        "api_version": "1.0.0",
        "uptime": "N/A",
        "requests_processed": "N/A",
        "status": "operational"
    }

@app.post("/graphql")
async def graphql_endpoint(request: Request):
    """GraphQL endpoint for complex workflow queries"""
    try:
        body = await request.json()
        query = body.get("query", "")
        variables = body.get("variables", {})
        
        # Simple GraphQL-like response for testing
        if "health" in query.lower():
            return {
                "data": {
                    "health": {
                        "status": "healthy",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
        elif "workflow" in query.lower():
            return {
                "data": {
                    "workflow": {
                        "status": "ready",
                        "agents": ["cleaner", "orchestrator"],
                        "version": "1.0.0"
                    }
                }
            }
        else:
            return {
                "data": {
                    "message": "GraphQL endpoint operational",
                    "supportedQueries": ["health", "workflow"]
                }
            }
            
    except Exception as e:
        logger.error(f"GraphQL endpoint error: {e}")
        raise HTTPException(status_code=400, detail=f"GraphQL error: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "message": "The requested endpoint does not exist"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    print("🚀 Starting Agentic Finance Workflow API Server...")
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
