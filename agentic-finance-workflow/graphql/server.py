"""
GraphQL Server for Agentic Finance Workflow

Provides a unified GraphQL API for all data operations including:
- Stock price queries
- Portfolio management
- Workflow execution and monitoring
- Real-time subscriptions
- Data quality reporting
"""

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, AsyncGenerator
import asyncio
from datetime import datetime
import json
import logging

from .resolvers.stock_resolvers import StockQueries, StockMutations, StockSubscriptions
from .resolvers.portfolio_resolvers import PortfolioQueries, PortfolioMutations
from .resolvers.workflow_resolvers import WorkflowQueries, WorkflowMutations, WorkflowSubscriptions
from .resolvers.system_resolvers import SystemQueries


logger = logging.getLogger(__name__)


@strawberry.type
class Query:
    """Root Query type combining all query resolvers"""
    
    # Stock data queries
    stock_prices: List["StockPrice"] = strawberry.field(resolver=StockQueries.get_stock_prices)
    stock_price: Optional["StockPrice"] = strawberry.field(resolver=StockQueries.get_stock_price)
    latest_stock_price: Optional["StockPrice"] = strawberry.field(resolver=StockQueries.get_latest_stock_price)
    stock_history: List["StockPrice"] = strawberry.field(resolver=StockQueries.get_stock_history)
    
    # Portfolio queries
    portfolios: List["Portfolio"] = strawberry.field(resolver=PortfolioQueries.get_portfolios)
    portfolio: Optional["Portfolio"] = strawberry.field(resolver=PortfolioQueries.get_portfolio)
    portfolio_performance: Optional["PerformanceMetrics"] = strawberry.field(resolver=PortfolioQueries.get_portfolio_performance)
    
    # Workflow queries
    workflows: List["WorkflowExecution"] = strawberry.field(resolver=WorkflowQueries.get_workflows)
    workflow: Optional["WorkflowExecution"] = strawberry.field(resolver=WorkflowQueries.get_workflow)
    workflows_by_status: List["WorkflowExecution"] = strawberry.field(resolver=WorkflowQueries.get_workflows_by_status)
    
    # Recommendation queries
    recommendations: List["Recommendation"] = strawberry.field(resolver=WorkflowQueries.get_recommendations)
    recommendation: Optional["Recommendation"] = strawberry.field(resolver=WorkflowQueries.get_recommendation)
    market_insights: List["MarketInsight"] = strawberry.field(resolver=WorkflowQueries.get_market_insights)
    
    # Data quality queries
    data_quality_report: Optional["DataQualityReport"] = strawberry.field(resolver=WorkflowQueries.get_data_quality_report)
    data_quality_history: List["DataQualityReport"] = strawberry.field(resolver=WorkflowQueries.get_data_quality_history)
    
    # System health
    system_health: "SystemHealth" = strawberry.field(resolver=SystemQueries.get_system_health)
    agent_status: List["AgentStatus"] = strawberry.field(resolver=SystemQueries.get_agent_status)


@strawberry.type
class Mutation:
    """Root Mutation type combining all mutation resolvers"""
    
    # Data ingestion
    upload_dataset: "DatasetUploadResult" = strawberry.field(resolver=StockMutations.upload_dataset)
    delete_dataset: bool = strawberry.field(resolver=StockMutations.delete_dataset)
    
    # Portfolio management
    create_portfolio: "Portfolio" = strawberry.field(resolver=PortfolioMutations.create_portfolio)
    update_portfolio: "Portfolio" = strawberry.field(resolver=PortfolioMutations.update_portfolio)
    delete_portfolio: bool = strawberry.field(resolver=PortfolioMutations.delete_portfolio)
    
    # Workflow management
    start_workflow: "WorkflowExecution" = strawberry.field(resolver=WorkflowMutations.start_workflow)
    stop_workflow: bool = strawberry.field(resolver=WorkflowMutations.stop_workflow)
    retry_workflow: "WorkflowExecution" = strawberry.field(resolver=WorkflowMutations.retry_workflow)
    
    # Recommendation management
    dismiss_recommendation: bool = strawberry.field(resolver=WorkflowMutations.dismiss_recommendation)
    execute_recommendation: "RecommendationResult" = strawberry.field(resolver=WorkflowMutations.execute_recommendation)
    
    # Data management
    clean_data: "DataCleaningResult" = strawberry.field(resolver=WorkflowMutations.clean_data)
    validate_data: "DataValidationResult" = strawberry.field(resolver=WorkflowMutations.validate_data)


@strawberry.type
class Subscription:
    """Root Subscription type for real-time updates"""
    
    # Real-time price updates
    @strawberry.subscription
    async def stock_price_updates(self, symbols: List[str]) -> AsyncGenerator["StockPrice", None]:
        """Subscribe to real-time stock price updates"""
        async for price_update in StockSubscriptions.stock_price_updates(symbols):
            yield price_update
    
    # Workflow progress
    @strawberry.subscription
    async def workflow_progress(self, workflow_id: str) -> AsyncGenerator["WorkflowExecution", None]:
        """Subscribe to workflow execution progress"""
        async for workflow_update in WorkflowSubscriptions.workflow_progress(workflow_id):
            yield workflow_update
    
    @strawberry.subscription
    async def agent_progress(self, workflow_id: str, agent_type: str) -> AsyncGenerator["AgentExecution", None]:
        """Subscribe to individual agent progress"""
        async for agent_update in WorkflowSubscriptions.agent_progress(workflow_id, agent_type):
            yield agent_update
    
    # Recommendations
    @strawberry.subscription
    async def new_recommendations(self, portfolios: Optional[List[str]] = None) -> AsyncGenerator["Recommendation", None]:
        """Subscribe to new recommendations"""
        async for recommendation in WorkflowSubscriptions.new_recommendations(portfolios):
            yield recommendation
    
    @strawberry.subscription
    async def market_insight_updates(self) -> AsyncGenerator["MarketInsight", None]:
        """Subscribe to market insight updates"""
        async for insight in WorkflowSubscriptions.market_insight_updates():
            yield insight
    
    # System monitoring
    @strawberry.subscription
    async def system_metrics(self) -> AsyncGenerator["SystemMetrics", None]:
        """Subscribe to system performance metrics"""
        async for metrics in SystemQueries.system_metrics():
            yield metrics
    
    @strawberry.subscription
    async def data_quality_alerts(self) -> AsyncGenerator["DataQualityAlert", None]:
        """Subscribe to data quality alerts"""
        async for alert in WorkflowSubscriptions.data_quality_alerts():
            yield alert


# Create GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)


def create_graphql_app(debug: bool = False, orchestrator=None) -> FastAPI:
    """
    Create FastAPI application with GraphQL endpoint
    
    Args:
        debug: Enable debug mode
        orchestrator: Orchestrator agent instance for workflow management
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Agentic Finance Workflow GraphQL API",
        description="Advanced financial data processing with AI agents",
        version="1.0.0",
        debug=debug
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create GraphQL router
    graphql_app = GraphQLRouter(
        schema,
        subscription_protocols=[
            GRAPHQL_TRANSPORT_WS_PROTOCOL,
            GRAPHQL_WS_PROTOCOL,
        ],
        debug=debug
    )
    
    # Include GraphQL router
    app.include_router(graphql_app, prefix="/graphql")
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "agentic-finance-graphql",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
    
    # API info endpoint
    @app.get("/")
    async def api_info():
        return {
            "service": "Agentic Finance Workflow GraphQL API",
            "version": "1.0.0",
            "endpoints": {
                "graphql": "/graphql",
                "playground": "/graphql" if debug else None,
                "health": "/health",
                "docs": "/docs"
            },
            "features": [
                "Stock price queries and subscriptions",
                "Portfolio management and analysis",
                "Workflow execution and monitoring",
                "Real-time recommendations",
                "Data quality monitoring",
                "System health monitoring"
            ]
        }
    
    # Store orchestrator reference for resolvers
    app.state.orchestrator = orchestrator
    
    logger.info("GraphQL application created successfully")
    return app


# Context injection for resolvers
@strawberry.field
def get_context_orchestrator(info) -> Optional[object]:
    """Get orchestrator from GraphQL context"""
    return getattr(info.context.get("request", {}).app.state, "orchestrator", None)


if __name__ == "__main__":
    import uvicorn
    
    # Create application
    app = create_graphql_app(debug=True)
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=4000,
        log_level="info"
    )
