# Agentic Finance Workflow - Development Guide

## Development Environment Setup

This guide covers setting up a development environment for contributing to the Agentic Finance Workflow project.

## Prerequisites

- **Python 3.9+**: Latest version recommended
- **Git**: Version control
- **Docker**: For containerized development
- **Node.js 16+**: For frontend development
- **PostgreSQL**: Database (can use Docker)
- **Redis**: Caching and message queuing

## Environment Setup

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/your-org/agentic-finance-workflow.git
cd agentic-finance-workflow

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env.dev

# Edit development configuration
# Key settings for development:
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://localhost:5432/agentic_finance_dev
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Setup

```bash
# Start PostgreSQL (Docker)
docker run -d \
  --name postgres-dev \
  -e POSTGRES_DB=agentic_finance_dev \
  -e POSTGRES_USER=dev \
  -e POSTGRES_PASSWORD=dev \
  -p 5432:5432 \
  postgres:13

# Start Redis (Docker)
docker run -d \
  --name redis-dev \
  -p 6379:6379 \
  redis:6-alpine

# Initialize database
python scripts/setup_database.py --env dev
```

## Project Structure

### Directory Organization

```text
agentic-finance-workflow/
├── agents/                 # Agent implementations
│   ├── __init__.py        # Base agent classes
│   ├── cleaner/           # Data cleaning agents
│   ├── validator/         # Data validation agents
│   ├── analyzer/          # Financial analysis agents
│   ├── visualizer/        # Visualization agents
│   ├── recommender/       # Recommendation agents
│   └── orchestrator/      # Workflow orchestration
├── graphql/               # GraphQL schema and resolvers
│   ├── schema.graphql     # GraphQL schema definition
│   ├── resolvers/         # GraphQL resolvers
│   └── server.py          # GraphQL server implementation
├── workflows/             # Workflow definitions
│   ├── templates/         # Pre-built workflow templates
│   └── custom/            # Custom workflow definitions
├── frontend/              # React frontend application
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   └── package.json       # Dependencies
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── configs/               # Configuration files
│   ├── development.yaml   # Development settings
│   ├── production.yaml    # Production settings
│   └── agents/            # Agent-specific configs
├── scripts/               # Utility scripts
│   ├── setup_database.py  # Database initialization
│   ├── seed_data.py       # Sample data generation
│   └── deployment/        # Deployment scripts
├── docs/                  # Documentation
├── docker/                # Docker configurations
├── kubernetes/            # Kubernetes manifests
└── requirements*.txt      # Python dependencies
```

### Key Modules

#### 1. Agents Module (`agents/`)

Base agent architecture:

```python
# agents/__init__.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import logging

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.metrics = AgentMetrics()
    
    @abstractmethod
    async def _process(self, input_data: Dict[str, Any], 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Core processing logic - must be implemented by subclasses"""
        pass
    
    async def execute(self, input_data: Dict[str, Any], 
                     context: Dict[str, Any]) -> AgentResult:
        """Main execution method with error handling and metrics"""
        pass
```

#### 2. GraphQL Module (`graphql/`)

Schema-first GraphQL implementation:

```python
# graphql/resolvers/agent_resolvers.py
import strawberry
from typing import List, Optional

@strawberry.type
class Agent:
    id: str
    type: str
    status: str
    
@strawberry.type
class Query:
    @strawberry.field
    async def agents(self) -> List[Agent]:
        """Get list of available agents"""
        pass
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def execute_agent(self, input: AgentExecutionInput) -> AgentResult:
        """Execute an agent with given input"""
        pass
```

#### 3. Workflow Module (`workflows/`)

Workflow definition and execution:

```python
# workflows/engine.py
class WorkflowEngine:
    """Executes workflows with dependency resolution"""
    
    async def execute_workflow(self, workflow_def: WorkflowDefinition,
                              input_data: Dict[str, Any]) -> WorkflowResult:
        """Execute workflow with parallel agent coordination"""
        pass
```

## Development Workflow

### 1. Code Style and Standards

We use comprehensive tooling for code quality:

```bash
# Install development tools (included in requirements-dev.txt)
pip install black isort flake8 mypy pytest pytest-asyncio pytest-cov

# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Run tests
pytest tests/ -v --cov=agents --cov-report=html
```

### 2. Pre-commit Hooks

Configured in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

### 3. Testing Strategy

#### Unit Tests

```python
# tests/unit/test_cleaner_agent.py
import pytest
from unittest.mock import Mock, AsyncMock
from agents.cleaner import DataCleanerAgent

@pytest.fixture
async def cleaner_agent():
    config = {
        "missing_value_strategy": "interpolate",
        "outlier_threshold": 3.0
    }
    return DataCleanerAgent(config)

@pytest.mark.asyncio
async def test_basic_cleaning(cleaner_agent, sample_data):
    """Test basic data cleaning functionality"""
    context = {"execution_id": "test_123"}
    result = await cleaner_agent.execute(sample_data, context)
    
    assert result.status == "completed"
    assert "cleaned_data" in result.output
    assert result.output["quality_score"] > 0.8
```

#### Integration Tests

```python
# tests/integration/test_workflow_execution.py
@pytest.mark.asyncio
async def test_complete_workflow():
    """Test end-to-end workflow execution"""
    workflow_def = load_workflow_template("financial-analysis-pipeline")
    input_data = load_sample_financial_data()
    
    engine = WorkflowEngine()
    result = await engine.execute_workflow(workflow_def, input_data)
    
    assert result.status == "completed"
    assert len(result.agent_results) == 5  # All agents executed
```

#### End-to-End Tests

```python
# tests/e2e/test_api_endpoints.py
import httpx
import pytest

@pytest.mark.asyncio
async def test_workflow_api_flow():
    """Test complete API workflow"""
    async with httpx.AsyncClient() as client:
        # Upload data
        upload_response = await client.post("/api/data/upload", files={"file": sample_csv})
        assert upload_response.status_code == 200
        
        # Start workflow
        workflow_response = await client.post("/graphql", json={
            "query": START_WORKFLOW_MUTATION,
            "variables": {"input": workflow_input}
        })
        assert workflow_response.status_code == 200
```

## Agent Development

### Creating a New Agent

1. **Create agent directory and files**:

```bash
mkdir agents/my_agent
touch agents/my_agent/__init__.py
touch agents/my_agent/config.py
touch agents/my_agent/processor.py
```

2. **Implement the agent**:

```python
# agents/my_agent/__init__.py
from typing import Dict, Any
from agents import BaseAgent, AgentResult

class MyCustomAgent(BaseAgent):
    """Custom agent for specific financial analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.processor = MyProcessor(config)
    
    async def _validate_input(self, input_data: Dict[str, Any], 
                             context: Dict[str, Any]) -> bool:
        """Validate input data format and requirements"""
        required_fields = ["data", "symbol"]
        return all(field in input_data for field in required_fields)
    
    async def _process(self, input_data: Dict[str, Any], 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Core processing logic"""
        df = input_data["data"]
        symbol = input_data["symbol"]
        
        # Your custom processing logic
        results = await self.processor.analyze(df, symbol)
        
        return {
            "analysis_results": results,
            "symbol": symbol,
            "processed_rows": len(df)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Agent-specific health checks"""
        return {
            "status": "healthy",
            "processor_ready": self.processor.is_ready(),
            "memory_usage": self.get_memory_usage()
        }
```

3. **Add configuration schema**:

```python
# agents/my_agent/config.py
from typing import Dict, Any
from pydantic import BaseModel, Field

class MyAgentConfig(BaseModel):
    """Configuration schema for MyCustomAgent"""
    
    analysis_type: str = Field(..., description="Type of analysis to perform")
    lookback_period: int = Field(252, description="Number of days to analyze")
    confidence_threshold: float = Field(0.95, description="Confidence threshold")
    enable_caching: bool = Field(True, description="Enable result caching")
    
    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> "MyAgentConfig":
        """Create config from dictionary"""
        return cls(**config)
```

4. **Write tests**:

```python
# tests/unit/test_my_agent.py
import pytest
from agents.my_agent import MyCustomAgent

@pytest.fixture
def agent_config():
    return {
        "analysis_type": "custom",
        "lookback_period": 100,
        "confidence_threshold": 0.9
    }

@pytest.fixture
async def my_agent(agent_config):
    return MyCustomAgent(agent_config)

@pytest.mark.asyncio
async def test_my_agent_execution(my_agent, sample_financial_data):
    """Test agent execution with sample data"""
    context = {"execution_id": "test_my_agent"}
    result = await my_agent.execute(sample_financial_data, context)
    
    assert result.status == "completed"
    assert "analysis_results" in result.output
```

5. **Register the agent**:

```python
# agents/__init__.py
from .my_agent import MyCustomAgent

# Agent registry
AGENT_REGISTRY = {
    "DataCleanerAgent": DataCleanerAgent,
    "FinancialAnalyzerAgent": FinancialAnalyzerAgent,
    "MyCustomAgent": MyCustomAgent,  # Add your agent here
}
```

### Agent Best Practices

#### 1. Error Handling

```python
async def _process(self, input_data: Dict[str, Any], 
                  context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Processing logic
        result = await self.do_processing(input_data)
        return result
    except ValidationError as e:
        self.logger.error(f"Input validation failed: {e}")
        raise AgentExecutionError(f"Invalid input: {e}")
    except Exception as e:
        self.logger.error(f"Unexpected error in processing: {e}")
        raise AgentExecutionError(f"Processing failed: {e}")
```

#### 2. Progress Reporting

```python
async def _process(self, input_data: Dict[str, Any], 
                  context: Dict[str, Any]) -> Dict[str, Any]:
    steps = ["validate", "transform", "analyze", "format"]
    total_steps = len(steps)
    
    for i, step in enumerate(steps):
        progress = (i + 1) / total_steps
        await self.update_progress(context, progress, f"Executing {step}")
        
        # Execute step
        await self.execute_step(step, input_data)
```

#### 3. Resource Management

```python
class ResourceManagedAgent(BaseAgent):
    async def __aenter__(self):
        """Async context manager entry"""
        await self.acquire_resources()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.release_resources()
    
    async def acquire_resources(self):
        """Acquire necessary resources"""
        self.connection_pool = await create_connection_pool()
        self.ml_model = await load_ml_model()
    
    async def release_resources(self):
        """Clean up resources"""
        if hasattr(self, 'connection_pool'):
            await self.connection_pool.close()
```

## GraphQL Development

### Adding New Types

1. **Define GraphQL schema** (`graphql/schema.graphql`):

```graphql
type TechnicalIndicator {
  name: String!
  value: Float!
  timestamp: DateTime!
  signal: IndicatorSignal
}

enum IndicatorSignal {
  BUY
  SELL
  HOLD
}

extend type Query {
  technicalIndicators(
    symbol: String!
    indicators: [String!]!
    period: Int = 20
  ): [TechnicalIndicator!]!
}
```

2. **Implement resolvers**:

```python
# graphql/resolvers/technical_indicators.py
import strawberry
from typing import List

@strawberry.type
class TechnicalIndicator:
    name: str
    value: float
    timestamp: datetime
    signal: Optional[IndicatorSignal]

@strawberry.enum
class IndicatorSignal:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

async def get_technical_indicators(
    symbol: str,
    indicators: List[str],
    period: int = 20
) -> List[TechnicalIndicator]:
    """Resolver for technical indicators query"""
    # Implementation logic
    pass
```

### Adding Subscriptions

```python
# graphql/resolvers/subscriptions.py
import strawberry
from typing import AsyncGenerator

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def agent_progress(
        self, 
        execution_id: str
    ) -> AsyncGenerator[AgentProgress, None]:
        """Subscribe to agent execution progress"""
        async for progress in self.agent_progress_stream(execution_id):
            yield progress
```

## Frontend Development

### Setup Frontend Development

```bash
cd frontend
npm install
npm start  # Development server on http://localhost:3000
```

### Key Components

#### 1. Workflow Dashboard

```typescript
// frontend/src/components/WorkflowDashboard.tsx
import React, { useEffect, useState } from 'react';
import { useSubscription, useMutation } from '@apollo/client';

const WorkflowDashboard: React.FC = () => {
  const [workflows, setWorkflows] = useState([]);
  
  const { data: progressData } = useSubscription(WORKFLOW_PROGRESS_SUBSCRIPTION);
  const [startWorkflow] = useMutation(START_WORKFLOW_MUTATION);
  
  return (
    <div className="workflow-dashboard">
      {/* Dashboard implementation */}
    </div>
  );
};
```

#### 2. Real-time Charts

```typescript
// frontend/src/components/FinancialChart.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface FinancialChartProps {
  data: FinancialDataPoint[];
  indicators?: TechnicalIndicator[];
}

const FinancialChart: React.FC<FinancialChartProps> = ({ data, indicators }) => {
  return (
    <LineChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="timestamp" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="close" stroke="#8884d8" />
      {indicators?.map(indicator => (
        <Line 
          key={indicator.name}
          type="monotone" 
          dataKey={indicator.name} 
          stroke={indicator.color} 
        />
      ))}
    </LineChart>
  );
};
```

## Debugging and Troubleshooting

### 1. Development Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Async debugging
import asyncio
import aiotools
aiotools.set_trace()
```

### 2. Performance Profiling

```python
# Profile agent execution
import cProfile
import pstats

async def profile_agent_execution():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Execute agent
    result = await agent.execute(input_data, context)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

### 3. Memory Monitoring

```python
# Monitor memory usage
import psutil
import tracemalloc

tracemalloc.start()

# Your code here

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

## Deployment and DevOps

### Local Development Stack

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  app:
    build:
      context: .
      dockerfile: docker/Dockerfile.dev
    volumes:
      - .:/app
      - /app/venv  # Exclude virtual environment
    environment:
      - DEBUG=true
      - RELOAD=true
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: agentic_finance_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_dev_data:
```

### CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=agents --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

This development guide provides a comprehensive foundation for contributing to the Agentic Finance Workflow project. Follow the coding standards, testing practices, and architectural patterns outlined here for consistent and maintainable code.
