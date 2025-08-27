# Contributing to Agentic Finance Workflow

We're excited that you're interested in contributing to the Agentic Finance Workflow project! This document outlines the guidelines and processes for contributing to our enterprise-grade financial data processing platform.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Security](#security)
- [Performance](#performance)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@agentic-finance.com](mailto:conduct@agentic-finance.com).

## Getting Started

### Ways to Contribute

- **Code Contributions**: Bug fixes, new features, performance improvements
- **Documentation**: API docs, tutorials, architecture guides, examples
- **Testing**: Writing tests, improving test coverage, performance testing
- **Bug Reports**: Detailed bug reports with reproduction steps
- **Feature Requests**: Well-defined feature proposals with use cases
- **Community Support**: Helping other users, answering questions

### Prerequisites

Before contributing, ensure you have:

- Python 3.9 or higher
- Git knowledge and GitHub account
- Understanding of async Python programming
- Familiarity with financial data concepts
- Docker for containerized development (recommended)

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/agentic-finance-workflow.git
cd agentic-finance-workflow

# Add upstream remote
git remote add upstream https://github.com/original-org/agentic-finance-workflow.git
```

### 2. Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env.dev
# Edit .env.dev with your development configuration
```

### 3. Development Services

```bash
# Start development services with Docker
docker-compose -f docker-compose.dev.yml up -d

# Or start services individually
# PostgreSQL
docker run -d --name postgres-dev -e POSTGRES_DB=agentic_finance_dev -p 5432:5432 postgres:13

# Redis
docker run -d --name redis-dev -p 6379:6379 redis:6-alpine
```

### 4. Verify Setup

```bash
# Run tests to verify setup
pytest tests/unit/ -v

# Check code quality
make lint

# Start development server
python main.py --mode api --env development
```

## Contributing Guidelines

### Issue Workflow

#### Before Creating an Issue

1. **Search existing issues** to avoid duplicates
2. **Check the roadmap** to see if the feature is planned
3. **Review documentation** to ensure it's not a usage question

#### Creating Issues

**Bug Reports**

```markdown
## Bug Description
A clear description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.9.7]
- Docker version: [e.g. 20.10.8]
- Project version: [e.g. 1.2.3]

## Additional Context
Any other context about the problem.

## Error Logs
```
[Paste error logs here]
```
```

**Feature Requests**

```markdown
## Feature Description
A clear description of the feature you'd like to see.

## Problem Statement
What problem does this solve? What use case does it enable?

## Proposed Solution
How would you like this feature to work?

## Alternatives Considered
Other approaches you've considered.

## Additional Context
Any other context, screenshots, or examples.
```

### Branch Naming

Use descriptive branch names following this convention:

- **Features**: `feature/short-description`
- **Bug fixes**: `fix/issue-number-short-description`
- **Documentation**: `docs/what-you-are-documenting`
- **Refactoring**: `refactor/what-you-are-refactoring`
- **Performance**: `perf/what-you-are-optimizing`

Examples:
```bash
git checkout -b feature/risk-metrics-agent
git checkout -b fix/123-memory-leak-cleaner-agent
git checkout -b docs/api-reference-update
git checkout -b refactor/agent-base-class
```

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run the full test suite**:
   ```bash
   make test-all
   ```

3. **Check code quality**:
   ```bash
   make lint
   make type-check
   make security-check
   ```

4. **Update documentation** if needed

5. **Add/update tests** for your changes

### PR Template

```markdown
## Description
Brief description of the changes.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Related Issues
Closes #123
Related to #456

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots to help explain your changes.

## Performance Impact
Describe any performance implications of your changes.
```

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Comprehensive test coverage expected
4. **Documentation**: Updates must be included for user-facing changes
5. **Security**: Security implications reviewed for sensitive changes

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some project-specific conventions:

#### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy .
```

#### Naming Conventions

```python
# Classes: PascalCase
class DataCleanerAgent:
    pass

# Functions and variables: snake_case
def process_financial_data():
    pass

def calculate_risk_metrics():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Private methods: leading underscore
def _internal_helper():
    pass

# Agent types: suffix with "Agent"
class CustomAnalyzerAgent(BaseAgent):
    pass
```

#### Docstring Standards

Use Google-style docstrings:

```python
async def execute_workflow(
    self,
    workflow_def: WorkflowDefinition,
    input_data: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> WorkflowResult:
    """Execute a workflow with the given definition and input data.
    
    Args:
        workflow_def: The workflow definition containing agent configurations
        input_data: Input data to be processed by the workflow
        context: Optional execution context with metadata
        
    Returns:
        WorkflowResult containing execution status and agent outputs
        
    Raises:
        WorkflowExecutionError: If workflow execution fails
        ValidationError: If input data is invalid
        
    Example:
        >>> workflow_def = load_workflow_template("risk-analysis")
        >>> input_data = {"portfolio": portfolio_data}
        >>> result = await executor.execute_workflow(workflow_def, input_data)
        >>> print(f"Status: {result.status}")
    """
```

#### Type Hints

All public functions must have type hints:

```python
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import pandas as pd

async def clean_financial_data(
    data: pd.DataFrame,
    config: Dict[str, Any],
    start_date: Optional[datetime] = None
) -> pd.DataFrame:
    """Clean financial data with the provided configuration."""
    pass
```

#### Error Handling

Use specific exception types and proper error handling:

```python
class AgentExecutionError(Exception):
    """Raised when agent execution fails."""
    
    def __init__(self, message: str, agent_type: str, execution_id: str):
        super().__init__(message)
        self.agent_type = agent_type
        self.execution_id = execution_id

# In agent code
try:
    result = await self._process(input_data, context)
except ValidationError as e:
    self.logger.error(f"Input validation failed: {e}")
    raise AgentExecutionError(
        f"Invalid input for {self.__class__.__name__}: {e}",
        self.__class__.__name__,
        context.get("execution_id", "unknown")
    )
```

### Agent Development Standards

#### Base Agent Implementation

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
import asyncio

class BaseAgent(ABC):
    """Base class for all financial processing agents."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate agent configuration."""
        required_fields = self.get_required_config_fields()
        missing_fields = [field for field in required_fields if field not in self.config]
        if missing_fields:
            raise ValueError(f"Missing required config fields: {missing_fields}")
    
    @abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """Return list of required configuration fields."""
        pass
    
    @abstractmethod
    async def _process(
        self, 
        input_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Core processing logic - must be implemented by subclasses."""
        pass
    
    async def execute(
        self, 
        input_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> AgentResult:
        """Execute agent with comprehensive error handling and metrics."""
        start_time = datetime.utcnow()
        
        try:
            # Validation
            await self._validate_input(input_data, context)
            
            # Processing
            output = await self._process(input_data, context)
            
            # Post-processing
            validated_output = await self._validate_output(output, context)
            
            return AgentResult(
                agent_type=self.__class__.__name__,
                status=AgentStatus.COMPLETED,
                output=validated_output,
                start_time=start_time,
                end_time=datetime.utcnow(),
                execution_id=context.get("execution_id")
            )
            
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            return AgentResult(
                agent_type=self.__class__.__name__,
                status=AgentStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=datetime.utcnow(),
                execution_id=context.get("execution_id")
            )
```

## Testing Requirements

### Test Coverage Standards

- **Minimum Coverage**: 85% overall, 90% for core agent logic
- **Critical Paths**: 100% coverage for data validation and error handling
- **Integration Tests**: All agent interactions must be tested
- **Performance Tests**: Memory and CPU usage benchmarks

### Test Categories

#### 1. Unit Tests

Test individual components in isolation:

```python
# tests/unit/test_cleaner_agent.py
import pytest
import pandas as pd
from unittest.mock import Mock, AsyncMock
from agents.cleaner import DataCleanerAgent

@pytest.fixture
def sample_financial_data():
    """Create sample financial data for testing."""
    return pd.DataFrame({
        'symbol': ['AAPL', 'AAPL', 'AAPL'],
        'timestamp': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        'open': [150.0, None, 152.0],  # Missing value for testing
        'close': [151.0, 151.5, 153.0],
        'volume': [1000000, 1200000, 950000]
    })

@pytest.fixture
def cleaner_config():
    """Create cleaner agent configuration."""
    return {
        "missing_value_strategy": "interpolate",
        "outlier_threshold": 3.0,
        "quality_threshold": 0.8
    }

@pytest.fixture
async def cleaner_agent(cleaner_config):
    """Create cleaner agent instance."""
    return DataCleanerAgent(cleaner_config)

@pytest.mark.asyncio
async def test_missing_value_handling(cleaner_agent, sample_financial_data):
    """Test missing value interpolation."""
    context = {"execution_id": "test_missing_values"}
    input_data = {"data": sample_financial_data}
    
    result = await cleaner_agent.execute(input_data, context)
    
    assert result.status == "completed"
    cleaned_data = result.output["cleaned_data"]
    assert not cleaned_data["open"].isna().any()
    assert cleaned_data.loc[1, "open"] == 151.0  # Interpolated value
```

#### 2. Integration Tests

Test component interactions:

```python
# tests/integration/test_workflow_execution.py
@pytest.mark.asyncio
async def test_complete_financial_analysis_workflow():
    """Test end-to-end workflow execution."""
    # Setup
    workflow_def = load_workflow_template("financial-analysis-pipeline")
    input_data = load_sample_market_data()
    
    # Execute
    engine = WorkflowEngine()
    result = await engine.execute_workflow(workflow_def, input_data)
    
    # Verify
    assert result.status == "completed"
    assert len(result.agent_results) == 5
    
    # Check each agent completed successfully
    agent_types = {r.agent_type for r in result.agent_results}
    expected_agents = {
        "DataCleanerAgent", 
        "DataValidatorAgent", 
        "FinancialAnalyzerAgent",
        "VisualizationAgent", 
        "RecommendationAgent"
    }
    assert agent_types == expected_agents
```

#### 3. Performance Tests

Benchmark critical operations:

```python
# tests/performance/test_agent_performance.py
import pytest
import time
import psutil
from agents.cleaner import DataCleanerAgent

@pytest.mark.benchmark
def test_cleaner_agent_performance(benchmark, large_financial_dataset):
    """Benchmark data cleaner agent performance."""
    
    def run_cleaning():
        agent = DataCleanerAgent({"missing_value_strategy": "interpolate"})
        context = {"execution_id": "perf_test"}
        return asyncio.run(agent.execute(large_financial_dataset, context))
    
    # Benchmark execution
    result = benchmark(run_cleaning)
    
    # Performance assertions
    assert benchmark.stats.stats.mean < 5.0  # Max 5 seconds
    assert psutil.virtual_memory().percent < 80  # Max 80% memory
```

### Test Utilities

Common test utilities and fixtures:

```python
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@pytest.fixture
def sample_stock_data():
    """Generate realistic stock price data."""
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
    dates = dates[dates.dayofweek < 5]  # Business days only
    
    # Generate realistic price movements
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = 100 * np.exp(np.cumsum(returns))
    
    return pd.DataFrame({
        'symbol': 'AAPL',
        'timestamp': dates,
        'open': prices * (1 + np.random.normal(0, 0.001, len(dates))),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.005, len(dates)))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.005, len(dates)))),
        'close': prices,
        'volume': np.random.randint(500000, 2000000, len(dates))
    })

@pytest.fixture
def mock_market_data_api():
    """Mock external market data API."""
    with patch('external_apis.market_data.MarketDataAPI') as mock:
        mock.return_value.get_stock_prices.return_value = sample_stock_data()
        yield mock
```

## Documentation

### Documentation Requirements

All contributions must include appropriate documentation:

#### 1. Code Documentation

- **Docstrings**: All public classes and methods
- **Type hints**: All function signatures
- **Inline comments**: Complex logic and financial calculations

#### 2. API Documentation

- **GraphQL Schema**: All types, queries, mutations, subscriptions
- **REST Endpoints**: OpenAPI/Swagger documentation
- **Examples**: Real-world usage examples

#### 3. User Documentation

- **Feature Documentation**: How to use new features
- **Configuration**: Configuration options and examples
- **Troubleshooting**: Common issues and solutions

### Documentation Style

Use clear, concise language with practical examples:

```markdown
## Risk Metrics Agent

The Risk Metrics Agent calculates various risk measures for financial portfolios.

### Configuration

```yaml
RiskMetricsAgent:
  var_confidence_levels: [0.95, 0.99]
  lookback_period: 252  # Trading days
  correlation_method: "pearson"
  stress_scenarios: 
    - "2008_financial_crisis"
    - "covid_2020"
```

### Usage

```python
agent = RiskMetricsAgent(config)
result = await agent.execute({
    "portfolio": portfolio_data,
    "benchmark": "SPY"
}, context)

print(f"Portfolio VaR (95%): {result.output['var_95']}")
```

### Output Format

The agent returns a dictionary with the following structure:

- `var_95`: Value at Risk at 95% confidence level
- `var_99`: Value at Risk at 99% confidence level
- `expected_shortfall`: Expected shortfall (Conditional VaR)
- `sharpe_ratio`: Risk-adjusted return metric
- `max_drawdown`: Maximum observed loss from peak
```

## Security

### Security Considerations

When contributing, keep these security aspects in mind:

#### 1. Data Protection

- **PII Handling**: Never log or expose personally identifiable information
- **Financial Data**: Treat all financial data as sensitive
- **API Keys**: Never commit API keys or secrets

```python
# ❌ Bad
logger.info(f"Processing data for user {user_email}")
api_key = "sk-1234567890abcdef"  # Hardcoded secret

# ✅ Good  
logger.info(f"Processing data for user {hash(user_email)}")
api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
```

#### 2. Input Validation

- **SQL Injection**: Use parameterized queries
- **File Uploads**: Validate file types and content
- **Data Validation**: Validate all external inputs

```python
# ✅ Proper input validation
def validate_stock_symbol(symbol: str) -> str:
    """Validate and sanitize stock symbol."""
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string")
    
    symbol = symbol.upper().strip()
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        raise ValueError("Invalid symbol format")
    
    return symbol
```

#### 3. Error Handling

- **Information Disclosure**: Don't expose sensitive information in errors
- **Logging**: Be careful what you log

```python
# ❌ Bad - exposes internal details
except DatabaseError as e:
    raise APIError(f"Database query failed: {e.query}")

# ✅ Good - generic error message
except DatabaseError as e:
    logger.error(f"Database error: {e}", exc_info=True)
    raise APIError("Internal server error")
```

## Performance

### Performance Guidelines

#### 1. Memory Management

- **Large Datasets**: Use chunked processing
- **Memory Leaks**: Properly clean up resources
- **Caching**: Cache frequently accessed data

```python
# Process large datasets in chunks
async def process_large_dataset(df: pd.DataFrame, chunk_size: int = 10000):
    """Process large dataset in memory-efficient chunks."""
    results = []
    
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        chunk_result = await process_chunk(chunk)
        results.append(chunk_result)
        
        # Explicit garbage collection for large datasets
        if len(results) % 10 == 0:
            gc.collect()
    
    return pd.concat(results, ignore_index=True)
```

#### 2. Async Programming

- **I/O Operations**: Use async for all I/O
- **CPU-bound Tasks**: Use thread/process pools
- **Concurrency**: Leverage asyncio for concurrent operations

```python
# ✅ Proper async usage
async def fetch_multiple_stocks(symbols: List[str]) -> Dict[str, pd.DataFrame]:
    """Fetch data for multiple stocks concurrently."""
    tasks = [fetch_stock_data(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {
        symbol: result for symbol, result in zip(symbols, results)
        if not isinstance(result, Exception)
    }
```

#### 3. Database Operations

- **Connection Pooling**: Use connection pools
- **Batch Operations**: Batch database operations
- **Indexing**: Ensure proper database indexes

```python
# Batch database operations
async def save_analysis_results(results: List[AnalysisResult]):
    """Save analysis results in batches for better performance."""
    batch_size = 1000
    
    async with get_db_connection() as conn:
        for i in range(0, len(results), batch_size):
            batch = results[i:i + batch_size]
            await conn.executemany(INSERT_QUERY, [r.to_dict() for r in batch])
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Discord**: Real-time chat and community support
- **Email**: security@agentic-finance.com for security issues

### Getting Help

1. **Check Documentation**: Start with our comprehensive docs
2. **Search Issues**: See if your question has been asked before
3. **Ask in Discussions**: For general questions and help
4. **Join Discord**: For real-time community support

### Recognition

We recognize and appreciate all contributions:

- **Contributors File**: All contributors are listed in CONTRIBUTORS.md
- **Release Notes**: Significant contributions mentioned in releases
- **Community Spotlights**: Regular highlighting of community members

## License

By contributing to this project, you agree that your contributions will be licensed under the same [MIT License](LICENSE) that covers the project.

---

Thank you for contributing to Agentic Finance Workflow! Your contributions help make financial data processing more accessible and powerful for everyone.
