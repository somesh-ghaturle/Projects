#!/usr/bin/env python3
"""
Simplified FastAPI Server for Agentic Finance Workflow
Streamlined version for easy deployment and testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pydantic import BaseModel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Finance Workflow API",
    description="Simplified financial data processing API with AI agents",
    version="1.0.0"
)

# Add CORS middleware for web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnalysisRequest(BaseModel):
    data_type: str
    symbol: str = "AAPL"
    agent_name: str

class WorkflowRequest(BaseModel):
    workflow_type: str
    data: Dict[str, Any]

# Financial Data Agents
class DataCleanerAgent:
    """Agent for cleaning and validating financial data"""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = data.get('symbol', 'AAPL')
        logger.info(f"Data Cleaner Agent processing {symbol}")
        
        # Simulate data cleaning process
        cleaned_data = {
            "original_records": 100,
            "cleaned_records": 95,
            "removed_outliers": 3,
            "filled_missing": 2,
            "validation_status": "PASSED",
            "data_quality_score": 0.95,
            "issues_found": [
                "2 missing volume entries filled using interpolation",
                "1 price outlier detected and adjusted",
                "Date format standardized"
            ]
        }
        
        return {
            "agent": "data_cleaner",
            "symbol": symbol,
            "status": "success",
            "results": cleaned_data,
            "timestamp": datetime.now().isoformat()
        }

class RiskAnalysisAgent:
    """Agent for financial risk analysis"""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = data.get('symbol', 'AAPL')
        logger.info(f"Risk Analysis Agent processing {symbol}")
        
        # Simulate risk analysis
        risk_metrics = {
            "var_95": round(np.random.uniform(0.02, 0.05), 4),
            "var_99": round(np.random.uniform(0.03, 0.07), 4),
            "volatility": round(np.random.uniform(0.15, 0.35), 4),
            "beta": round(np.random.uniform(0.8, 1.5), 2),
            "sharpe_ratio": round(np.random.uniform(0.5, 2.0), 2),
            "maximum_drawdown": round(np.random.uniform(0.05, 0.25), 4),
            "risk_grade": np.random.choice(["LOW", "MEDIUM", "HIGH"]),
            "risk_factors": [
                "Market volatility exposure",
                "Sector concentration risk",
                "Liquidity risk assessment"
            ]
        }
        
        return {
            "agent": "risk_analysis",
            "symbol": symbol,
            "status": "success",
            "results": risk_metrics,
            "timestamp": datetime.now().isoformat()
        }

class PortfolioOptimizerAgent:
    """Agent for portfolio optimization"""
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        symbol = data.get('symbol', 'AAPL')
        logger.info(f"Portfolio Optimizer Agent processing {symbol}")
        
        # Simulate portfolio optimization
        optimization_results = {
            "optimal_weights": {
                "AAPL": 0.25,
                "GOOGL": 0.20,
                "MSFT": 0.20,
                "AMZN": 0.15,
                "TSLA": 0.10,
                "CASH": 0.10
            },
            "expected_return": round(np.random.uniform(0.08, 0.15), 4),
            "expected_volatility": round(np.random.uniform(0.12, 0.25), 4),
            "efficient_frontier_points": 50,
            "optimization_method": "Modern Portfolio Theory",
            "rebalancing_frequency": "Monthly",
            "constraints": {
                "max_position_size": 0.30,
                "min_position_size": 0.05,
                "sector_limits": "Technology: 60%"
            }
        }
        
        return {
            "agent": "portfolio_optimizer",
            "symbol": symbol,
            "status": "success",
            "results": optimization_results,
            "timestamp": datetime.now().isoformat()
        }

# Initialize agents
data_cleaner = DataCleanerAgent()
risk_analyzer = RiskAnalysisAgent()
portfolio_optimizer = PortfolioOptimizerAgent()

# Agent registry
AGENTS = {
    "data_cleaner": data_cleaner,
    "risk_analyzer": risk_analyzer,
    "portfolio_optimizer": portfolio_optimizer
}

@app.get("/")
async def root():
    return {
        "message": "Agentic Finance Workflow API",
        "version": "1.0.0",
        "status": "running",
        "available_agents": list(AGENTS.keys()),
        "endpoints": {
            "health": "/health",
            "agents": "/agent/{agent_name}",
            "workflow": "/workflow",
            "market_data": "/market-data/{symbol}"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Finance API is running successfully",
        "version": "1.0.0",
        "agents_available": len(AGENTS),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/agent/{agent_name}")
async def process_with_agent(agent_name: str, request: AnalysisRequest):
    if agent_name not in AGENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Available: {list(AGENTS.keys())}"
        )
    
    try:
        agent = AGENTS[agent_name]
        result = agent.process({
            "symbol": request.symbol,
            "data_type": request.data_type
        })
        return result
    except Exception as e:
        logger.error(f"Error processing with {agent_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow")
async def run_workflow(request: WorkflowRequest):
    """Run a complete workflow with multiple agents"""
    try:
        workflow_type = request.workflow_type
        symbol = request.data.get('symbol', 'AAPL')
        
        if workflow_type == "complete_analysis":
            # Run all agents in sequence
            results = {}
            
            # Step 1: Data Cleaning
            clean_result = data_cleaner.process({"symbol": symbol})
            results["data_cleaning"] = clean_result["results"]
            
            # Step 2: Risk Analysis
            risk_result = risk_analyzer.process({"symbol": symbol})
            results["risk_analysis"] = risk_result["results"]
            
            # Step 3: Portfolio Optimization
            portfolio_result = portfolio_optimizer.process({"symbol": symbol})
            results["portfolio_optimization"] = portfolio_result["results"]
            
            return {
                "workflow": workflow_type,
                "symbol": symbol,
                "status": "completed",
                "execution_time": "2.3s",
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
        
        elif workflow_type == "risk_assessment":
            # Risk-focused workflow
            clean_result = data_cleaner.process({"symbol": symbol})
            risk_result = risk_analyzer.process({"symbol": symbol})
            
            return {
                "workflow": workflow_type,
                "symbol": symbol,
                "status": "completed",
                "results": {
                    "data_quality": clean_result["results"]["data_quality_score"],
                    "risk_metrics": risk_result["results"]
                },
                "timestamp": datetime.now().isoformat()
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown workflow type: {workflow_type}. Available: complete_analysis, risk_assessment"
            )
            
    except Exception as e:
        logger.error(f"Workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-data/{symbol}")
async def get_market_data(symbol: str):
    """Generate sample market data for a symbol"""
    try:
        # Generate realistic market data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), periods=30, freq='D')
        base_price = np.random.uniform(100, 300)
        
        market_data = []
        for i, date in enumerate(dates):
            price = base_price + np.random.normal(0, base_price * 0.02)
            volume = int(np.random.uniform(1000000, 5000000))
            
            market_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(price * 0.995, 2),
                "high": round(price * 1.02, 2),
                "low": round(price * 0.98, 2),
                "close": round(price, 2),
                "volume": volume
            })
        
        return {
            "symbol": symbol,
            "data_points": len(market_data),
            "period": "30 days",
            "data": market_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Market data error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    return {
        "available_agents": {
            "data_cleaner": {
                "name": "Data Cleaner Agent",
                "description": "Cleans and validates financial data",
                "capabilities": ["outlier detection", "missing data handling", "validation"]
            },
            "risk_analyzer": {
                "name": "Risk Analysis Agent", 
                "description": "Performs comprehensive risk analysis",
                "capabilities": ["VaR calculation", "volatility analysis", "risk grading"]
            },
            "portfolio_optimizer": {
                "name": "Portfolio Optimizer Agent",
                "description": "Optimizes portfolio allocation",
                "capabilities": ["weight optimization", "efficient frontier", "constraint handling"]
            }
        },
        "total_agents": len(AGENTS)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
