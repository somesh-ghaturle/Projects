#!/usr/bin/env python3
"""
Production-Ready Agentic Finance Workflow API
Multi-agent financial analysis platform with professional web interface
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
import math
import os
import asyncio
from pathlib import Path
import json

# Utility function to sanitize data for JSON serialization
def sanitize_for_json(obj):
    """
    Recursively sanitize data structure to handle NaN, infinity, and numpy types
    """
    if isinstance(obj, dict):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif pd.isna(obj):
        return None
    else:
        return obj

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Finance Workflow API",
    description="Production-ready multi-agent financial analysis platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class AnalysisRequest(BaseModel):
    symbol: str = "AAPL"
    days: int = 30
    agent_type: str = "cleaner"

class WorkflowRequest(BaseModel):
    symbols: List[str] = ["AAPL", "GOOGL", "MSFT"]
    analysis_type: str = "comprehensive"
    days: int = 30

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    agents: Dict[str, str]

# Financial Data Generator
class FinancialDataGenerator:
    """Generate realistic financial data for testing and demonstration"""
    
    def __init__(self):
        self.stock_profiles = {
            # Tech Giants
            'AAPL': {'base_return': 0.12, 'volatility': 0.28, 'beta': 1.2, 'sector': 'Technology'},
            'GOOGL': {'base_return': 0.14, 'volatility': 0.32, 'beta': 1.1, 'sector': 'Technology'},
            'MSFT': {'base_return': 0.13, 'volatility': 0.26, 'beta': 0.9, 'sector': 'Technology'},
            'AMZN': {'base_return': 0.15, 'volatility': 0.35, 'beta': 1.3, 'sector': 'Technology'},
            'META': {'base_return': 0.16, 'volatility': 0.40, 'beta': 1.4, 'sector': 'Technology'},
            
            # Financial Services
            'JPM': {'base_return': 0.10, 'volatility': 0.22, 'beta': 1.1, 'sector': 'Financial'},
            'BAC': {'base_return': 0.09, 'volatility': 0.25, 'beta': 1.2, 'sector': 'Financial'},
            'WFC': {'base_return': 0.08, 'volatility': 0.27, 'beta': 1.3, 'sector': 'Financial'},
            
            # Healthcare
            'JNJ': {'base_return': 0.07, 'volatility': 0.15, 'beta': 0.7, 'sector': 'Healthcare'},
            'PFE': {'base_return': 0.06, 'volatility': 0.18, 'beta': 0.8, 'sector': 'Healthcare'},
            
            # Energy
            'XOM': {'base_return': 0.05, 'volatility': 0.30, 'beta': 1.0, 'sector': 'Energy'},
            'CVX': {'base_return': 0.04, 'volatility': 0.28, 'beta': 0.9, 'sector': 'Energy'},
        }
    
    def generate_market_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Generate realistic market data for a given symbol"""
        if symbol not in self.stock_profiles:
            symbol = 'AAPL'  # Default fallback
        
        profile = self.stock_profiles[symbol]
        base_price = 100 + np.random.uniform(50, 200)
        
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=days),
            periods=days,
            freq='D'
        )
        
        data = []
        current_price = base_price
        
        for date in dates:
            # Simulate realistic price movements
            daily_return = np.random.normal(
                profile['base_return'] / 252,  # Daily return
                profile['volatility'] / np.sqrt(252)  # Daily volatility
            )
            
            current_price *= (1 + daily_return)
            volatility = current_price * profile['volatility'] / np.sqrt(252) * np.random.uniform(0.5, 2.0)
            
            open_price = current_price * (1 + np.random.normal(0, 0.01))
            high_price = max(open_price, current_price) + abs(np.random.normal(0, volatility))
            low_price = min(open_price, current_price) - abs(np.random.normal(0, volatility))
            close_price = current_price
            volume = int(np.random.lognormal(15, 1))  # Realistic volume distribution
            
            data.append({
                'timestamp': date,
                'symbol': symbol,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'sector': profile['sector']
            })
        
        return pd.DataFrame(data)

# Financial Agents
class DataCleanerAgent:
    """Production-grade data cleaning agent"""
    
    def __init__(self):
        self.name = "DataCleanerAgent"
        self.version = "2.0.0"
    
    async def process(self, data: List[Dict]) -> Dict[str, Any]:
        """Clean and validate financial data"""
        try:
            df = pd.DataFrame(data)
            original_count = len(df)
            
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    df[col] = df[col].interpolate(method='linear')
            
            # Remove outliers using IQR method
            for col in ['open', 'high', 'low', 'close']:
                if col in df.columns:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            
            # Validate price relationships
            df = df[
                (df['high'] >= df['open']) & 
                (df['high'] >= df['close']) &
                (df['low'] <= df['open']) & 
                (df['low'] <= df['close']) &
                (df['volume'] > 0)
            ]
            
            cleaned_count = len(df)
            quality_score = min(cleaned_count / original_count, 1.0) if original_count > 0 else 0
            
            return {
                'status': 'success',
                'agent': self.name,
                'original_records': original_count,
                'cleaned_records': cleaned_count,
                'quality_score': round(quality_score, 2),
                'cleaned_data': df.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"DataCleanerAgent error: {e}")
            return {
                'status': 'error',
                'agent': self.name,
                'error': str(e),
                'cleaned_data': []
            }

class RiskAnalysisAgent:
    """Advanced risk analysis agent"""
    
    def __init__(self):
        self.name = "RiskAnalysisAgent"
        self.version = "2.0.0"
    
    async def process(self, data: List[Dict]) -> Dict[str, Any]:
        """Perform comprehensive risk analysis"""
        try:
            df = pd.DataFrame(data)
            if len(df) < 2:
                raise ValueError("Insufficient data for risk analysis")
            
            # Calculate returns
            df['returns'] = df['close'].pct_change().dropna()
            
            # Risk metrics
            volatility = df['returns'].std() * np.sqrt(252)  # Annualized
            var_95 = np.percentile(df['returns'], 5)
            var_99 = np.percentile(df['returns'], 1)
            max_drawdown = ((df['close'] / df['close'].cummax()) - 1).min()
            sharpe_ratio = (df['returns'].mean() * 252) / (df['returns'].std() * np.sqrt(252))
            
            return {
                'status': 'success',
                'agent': self.name,
                'risk_metrics': {
                    'volatility': round(volatility, 4),
                    'var_95': round(var_95, 4),
                    'var_99': round(var_99, 4),
                    'max_drawdown': round(max_drawdown, 4),
                    'sharpe_ratio': round(sharpe_ratio, 4)
                },
                'analysis_period': len(df),
                'symbol': df['symbol'].iloc[0] if 'symbol' in df.columns else 'UNKNOWN'
            }
            
        except Exception as e:
            logger.error(f"RiskAnalysisAgent error: {e}")
            return {
                'status': 'error',
                'agent': self.name,
                'error': str(e)
            }

class PredictionAgent:
    """Advanced price prediction agent"""
    
    def __init__(self):
        self.name = "PredictionAgent"
        self.version = "2.0.0"
    
    async def process(self, data: List[Dict]) -> Dict[str, Any]:
        """Generate price predictions with confidence intervals"""
        try:
            df = pd.DataFrame(data)
            if len(df) < 10:
                raise ValueError("Insufficient data for prediction")
            
            # Simple trend analysis with confidence intervals
            prices = df['close'].values
            days = np.arange(len(prices))
            
            # Linear trend
            slope, intercept = np.polyfit(days, prices, 1)
            
            # Calculate residuals for confidence interval
            predicted = slope * days + intercept
            residuals = prices - predicted
            std_error = np.std(residuals)
            
            # Future predictions (next 5 days)
            future_days = np.arange(len(prices), len(prices) + 5)
            future_prices = slope * future_days + intercept
            
            # Confidence intervals
            confidence_95 = 1.96 * std_error
            upper_bound = future_prices + confidence_95
            lower_bound = future_prices - confidence_95
            
            predictions = []
            for i, day in enumerate(future_days):
                predictions.append({
                    'day': int(day - len(prices) + 1),
                    'predicted_price': round(future_prices[i], 2),
                    'upper_bound': round(upper_bound[i], 2),
                    'lower_bound': round(lower_bound[i], 2),
                    'confidence': 0.95
                })
            
            return {
                'status': 'success',
                'agent': self.name,
                'current_price': round(prices[-1], 2),
                'trend': 'bullish' if slope > 0 else 'bearish',
                'slope': round(slope, 4),
                'predictions': predictions,
                'model_accuracy': round(1 - (std_error / np.mean(prices)), 2)
            }
            
        except Exception as e:
            logger.error(f"PredictionAgent error: {e}")
            return {
                'status': 'error',
                'agent': self.name,
                'error': str(e)
            }

# Initialize components
data_generator = FinancialDataGenerator()
cleaner_agent = DataCleanerAgent()
risk_agent = RiskAnalysisAgent()
prediction_agent = PredictionAgent()

# Store start time for uptime calculation
start_time = datetime.now()

# API Endpoints

@app.get("/")
async def root():
    """Serve the professional web interface"""
    try:
        # Try to serve the professional interface first
        professional_path = Path("web_interface_professional.html")
        if professional_path.exists():
            return FileResponse("web_interface_professional.html", media_type="text/html")
        
        # Fallback to original interface
        original_path = Path("web_interface.html")
        if original_path.exists():
            return FileResponse("web_interface.html", media_type="text/html")
        
        # If no interface files exist, return a basic message
        return JSONResponse({
            "message": "Agentic Finance Workflow API",
            "version": "2.0.0",
            "status": "healthy",
            "endpoints": {
                "health": "/health",
                "analyze": "/analyze/{symbol}",
                "workflow": "/workflow",
                "market_data": "/market-data/{symbol}",
                "predict": "/predict/{symbol}",
                "docs": "/api/docs"
            }
        })
    except Exception as e:
        logger.error(f"Error serving interface: {e}")
        return JSONResponse({
            "message": "Agentic Finance Workflow API",
            "version": "2.0.0",
            "status": "healthy",
            "error": "Interface not available"
        })
    """Serve the professional web interface"""
    # Use the professional web interface
    interface_file = Path(__file__).parent / "web_interface.html"
    if interface_file.exists():
        return FileResponse(interface_file)
    
    # Fallback to create a basic interface if the file doesn't exist
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    
    html_file = static_dir / "index.html"
    if not html_file.exists():
        # Create a basic HTML interface if it doesn't exist
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agentic Finance Workflow</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .api-links { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; }
        .card h3 { margin-top: 0; color: #2c3e50; }
        .card a { color: #3498db; text-decoration: none; }
        .card a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Agentic Finance Workflow</h1>
            <p>Production-ready multi-agent financial analysis platform</p>
        </div>
        
        <div class="api-links">
            <div class="card">
                <h3>📊 API Documentation</h3>
                <p><a href="/api/docs">Interactive API Docs</a></p>
                <p><a href="/api/redoc">ReDoc Documentation</a></p>
            </div>
            
            <div class="card">
                <h3>💚 System Health</h3>
                <p><a href="/health">Health Check</a></p>
                <p><a href="/agents">Agent Status</a></p>
            </div>
            
            <div class="card">
                <h3>🔍 Analysis Endpoints</h3>
                <p><a href="/analyze/AAPL">Analyze AAPL</a></p>
                <p><a href="/workflow">Complete Workflow</a></p>
            </div>
            
            <div class="card">
                <h3>📈 Market Data</h3>
                <p><a href="/market-data/AAPL">AAPL Market Data</a></p>
                <p><a href="/predict/AAPL">AAPL Prediction</a></p>
            </div>
        </div>
    </div>
</body>
</html>"""
        html_file.write_text(html_content)
    
    return FileResponse(html_file)

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """System health check"""
    uptime = (datetime.now() - start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        service="Agentic Finance Workflow",
        version="2.0.0",
        uptime=round(uptime, 2),
        agents={
            "data_cleaner": "active",
            "risk_analysis": "active", 
            "prediction": "active",
            "data_generator": "active"
        }
    )

@app.get("/agents")
async def agent_status():
    """Get status of all agents"""
    return {
        "agents": [
            {"name": cleaner_agent.name, "version": cleaner_agent.version, "status": "active"},
            {"name": risk_agent.name, "version": risk_agent.version, "status": "active"},
            {"name": prediction_agent.name, "version": prediction_agent.version, "status": "active"}
        ],
        "total_agents": 3,
        "system_status": "operational"
    }

@app.get("/market-data/{symbol}")
async def get_market_data(symbol: str, days: int = 30):
    """Generate market data for a symbol"""
    try:
        df = data_generator.generate_market_data(symbol.upper(), days)
        result = {
            "symbol": symbol.upper(),
            "days": days,
            "records": len(df),
            "data": df.to_dict('records'),
            "latest_price": df['close'].iloc[-1] if len(df) > 0 else 0,
            "sector": df['sector'].iloc[0] if len(df) > 0 and 'sector' in df.columns else 'Unknown'
        }
        return sanitize_for_json(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/{symbol}")
async def analyze_symbol(symbol: str, request: AnalysisRequest):
    """Analyze a single symbol with specified agent"""
    try:
        # Generate market data
        df = data_generator.generate_market_data(symbol.upper(), request.days)
        data = df.to_dict('records')
        
        # Route to appropriate agent
        if request.agent_type == "cleaner":
            result = await cleaner_agent.process(data)
        elif request.agent_type == "risk":
            result = await risk_agent.process(data)
        elif request.agent_type == "prediction":
            result = await prediction_agent.process(data)
        else:
            raise HTTPException(status_code=400, detail="Invalid agent type")
        
        return sanitize_for_json(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow")
async def complete_workflow(request: WorkflowRequest):
    """Execute complete multi-agent workflow"""
    try:
        results = {}
        
        for symbol in request.symbols:
            # Generate data
            df = data_generator.generate_market_data(symbol.upper(), request.days)
            data = df.to_dict('records')
            
            # Execute all agents
            symbol_results = {
                'symbol': symbol.upper(),
                'data_cleaning': await cleaner_agent.process(data),
                'risk_analysis': await risk_agent.process(data),
                'prediction': await prediction_agent.process(data)
            }
            
            results[symbol.upper()] = symbol_results
        
        # Sanitize results before returning
        final_results = {
            'workflow_type': request.analysis_type,
            'symbols_analyzed': len(request.symbols),
            'total_agents': 3,
            'results': results,
            'execution_time': datetime.now().isoformat()
        }
        
        return sanitize_for_json(final_results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predict/{symbol}")
async def predict_prices(symbol: str, days: int = 30):
    """Get price predictions for a symbol"""
    try:
        df = data_generator.generate_market_data(symbol.upper(), days)
        data = df.to_dict('records')
        
        result = await prediction_agent.process(data)
        return sanitize_for_json(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Starting Agentic Finance Workflow API...")
    logger.info("📡 Server will be available at: http://localhost:8001")
    logger.info("📚 API Documentation: http://localhost:8001/api/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        reload=False  # Disable reload for production
    )
