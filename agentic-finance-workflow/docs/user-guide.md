# Agentic Finance Workflow - User Guide

## Getting Started

This guide will help you get up and running with the Agentic Finance Workflow system for financial data processing and analysis.

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL 13+ (if running locally)
- Redis 6+ (for caching and message queuing)

## Installation

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/agentic-finance-workflow.git
cd agentic-finance-workflow

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Option 2: Local Development Setup

```bash
# Clone and setup virtual environment
git clone https://github.com/your-org/agentic-finance-workflow.git
cd agentic-finance-workflow
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/setup_database.py

# Start the application
python main.py
```

## Quick Start

### 1. Access the Application

Once the services are running, you can access:

- **Web Dashboard**: http://localhost:3000
- **GraphQL API**: http://localhost:8000/graphql
- **API Documentation**: http://localhost:8000/docs

### 2. Your First Workflow

Let's create and run a simple financial analysis workflow:

#### Using the Web Dashboard

1. Navigate to http://localhost:3000
2. Login with the default credentials:
   - Email: `admin@example.com`
   - Password: `admin123`
3. Click "Create New Workflow"
4. Select "Financial Analysis Pipeline" template
5. Upload your financial data (CSV format)
6. Configure parameters and start execution

#### Using the API

```bash
# Login and get authentication token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Use the returned token for authenticated requests
export TOKEN="your-jwt-token"

# Start a workflow
curl -X POST http://localhost:8000/graphql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation StartWorkflow($input: WorkflowExecutionInput!) { startWorkflow(input: $input) { id status } }",
    "variables": {
      "input": {
        "workflowId": "financial-analysis-pipeline",
        "inputData": {
          "dataSource": "uploaded_file",
          "symbol": "AAPL"
        }
      }
    }
  }'
```

### 3. Monitor Execution

Track your workflow progress in real-time:

#### Web Dashboard
- Navigate to "Workflows" → "Executions"
- Click on your running workflow
- View real-time progress and agent outputs

#### API Subscription
```javascript
// WebSocket subscription for real-time updates
const subscription = `
  subscription WorkflowProgress($executionId: ID!) {
    workflowProgress(executionId: $executionId) {
      status
      completedSteps
      totalSteps
      currentAgent
    }
  }
`;
```

## Understanding Workflows

### Pre-built Workflow Templates

#### 1. Financial Analysis Pipeline
**Purpose**: Complete analysis of financial data
**Components**:
- Data Cleaner: Clean and validate input data
- Validator: Ensure data quality
- Analyzer: Calculate financial metrics
- Visualizer: Generate charts and reports
- Recommender: Provide investment insights

**Input**: Financial data (stocks, portfolios, market data)
**Output**: Analysis reports, visualizations, recommendations

#### 2. Risk Assessment Workflow
**Purpose**: Comprehensive risk analysis
**Components**:
- Data Cleaner: Prepare risk data
- Risk Analyzer: Calculate VaR, CVaR, correlation metrics
- Stress Tester: Scenario analysis
- Reporter: Risk reports and alerts

#### 3. Portfolio Optimization
**Purpose**: Optimize portfolio allocation
**Components**:
- Data Validator: Validate portfolio data
- Performance Analyzer: Historical performance analysis
- Optimizer: Modern Portfolio Theory optimization
- Backtester: Historical performance validation

### Creating Custom Workflows

#### Using YAML Configuration

Create a workflow definition file:

```yaml
# workflows/custom-analysis.yaml
name: "Custom Financial Analysis"
description: "Custom workflow for specific analysis needs"
version: "1.0"

parameters:
  - name: symbol
    type: string
    required: true
    description: "Stock symbol to analyze"
  - name: period
    type: integer
    default: 252
    description: "Analysis period in days"

agents:
  - type: DataCleanerAgent
    name: cleaner
    configuration:
      missing_value_strategy: "interpolate"
      outlier_threshold: 3.0
    
  - type: FinancialAnalyzerAgent
    name: analyzer
    dependencies: [cleaner]
    configuration:
      indicators: ["SMA", "RSI", "MACD"]
      period: "{{ parameters.period }}"
    
  - type: VisualizationAgent
    name: visualizer
    dependencies: [analyzer]
    configuration:
      chart_types: ["candlestick", "indicators"]
      output_format: "png"

outputs:
  - agent: analyzer
    name: "analysis_results"
    type: "json"
  - agent: visualizer
    name: "charts"
    type: "file"
```

#### Using Python API

```python
from agentic_finance_workflow import WorkflowBuilder, AgentConfig

# Create workflow programmatically
workflow = WorkflowBuilder("custom-analysis")

# Add agents
cleaner_config = AgentConfig(
    type="DataCleanerAgent",
    configuration={
        "missing_value_strategy": "interpolate",
        "outlier_threshold": 3.0
    }
)
workflow.add_agent("cleaner", cleaner_config)

analyzer_config = AgentConfig(
    type="FinancialAnalyzerAgent",
    dependencies=["cleaner"],
    configuration={
        "indicators": ["SMA", "RSI", "MACD"],
        "period": 252
    }
)
workflow.add_agent("analyzer", analyzer_config)

# Register workflow
workflow.register()
```

## Data Management

### Supported Data Formats

#### Input Formats
- **CSV**: Standard comma-separated values
- **JSON**: Structured JSON data
- **Parquet**: Columnar storage format
- **Excel**: .xlsx files (limited support)
- **API**: Direct integration with financial data providers

#### Required Data Schema

For stock price data:
```csv
symbol,timestamp,open,high,low,close,volume
AAPL,2024-01-01,150.00,152.50,149.50,151.00,1000000
AAPL,2024-01-02,151.00,153.00,150.00,152.50,1200000
```

For portfolio data:
```csv
symbol,quantity,average_price,market_price
AAPL,100,150.00,155.00
MSFT,50,300.00,310.00
GOOGL,25,2500.00,2600.00
```

### Data Upload Methods

#### Web Interface
1. Go to "Data" → "Upload"
2. Select file format
3. Choose file or drag-and-drop
4. Map columns to required schema
5. Validate and upload

#### API Upload
```bash
# Upload CSV file
curl -X POST http://localhost:8000/api/data/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@data.csv" \
  -F "format=csv" \
  -F "type=stock_prices"
```

#### Programmatic Upload
```python
from agentic_finance_workflow import DataUploader

uploader = DataUploader()
result = uploader.upload_file(
    file_path="data/stock_prices.csv",
    data_type="stock_prices",
    format="csv"
)
print(f"Upload ID: {result.upload_id}")
```

## Agent Configuration

### Data Cleaner Agent

```yaml
DataCleanerAgent:
  missing_value_strategy: "interpolate"  # interpolate, forward_fill, drop
  outlier_threshold: 3.0                 # Standard deviations
  duplicate_strategy: "remove"           # remove, keep_first, keep_last
  business_days_only: true               # Filter to business days
  quality_threshold: 0.8                 # Minimum quality score
```

### Financial Analyzer Agent

```yaml
FinancialAnalyzerAgent:
  indicators:
    - name: "SMA"
      period: 20
    - name: "RSI"
      period: 14
    - name: "MACD"
      fast: 12
      slow: 26
      signal: 9
  risk_metrics:
    - "volatility"
    - "sharpe_ratio"
    - "max_drawdown"
  lookback_period: 252
```

### Visualization Agent

```yaml
VisualizationAgent:
  chart_types:
    - "candlestick"
    - "line"
    - "indicators"
  output_formats: ["png", "pdf", "svg"]
  chart_size: [12, 8]
  theme: "professional"
  include_volume: true
```

## Monitoring and Troubleshooting

### Health Checks

Monitor system health:

```bash
# Check overall system health
curl http://localhost:8000/health

# Check specific agent health
curl http://localhost:8000/health/agents/DataCleanerAgent
```

### Logs and Debugging

#### Viewing Logs

```bash
# Docker deployment
docker-compose logs -f app

# Local deployment
tail -f logs/application.log
```

#### Log Levels

Configure log levels in your environment:

```bash
# In .env file
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

#### Common Issues and Solutions

**Issue**: Agent execution timeout
```bash
# Solution: Increase timeout in configuration
AGENT_TIMEOUT=300  # seconds
```

**Issue**: Database connection errors
```bash
# Solution: Check database credentials and connectivity
docker-compose logs postgres
```

**Issue**: Out of memory errors
```bash
# Solution: Increase Docker memory limits or use data chunking
CHUNK_SIZE=1000  # Process data in smaller chunks
```

### Performance Optimization

#### Memory Management

```python
# Configure chunked processing for large datasets
DataCleanerAgent:
  chunk_size: 10000      # Process 10k rows at a time
  memory_limit: "2GB"    # Maximum memory usage
```

#### Parallel Processing

```yaml
# Enable parallel agent execution
OrchestratorAgent:
  max_parallel_agents: 4
  enable_parallel_execution: true
```

## Advanced Features

### Custom Agent Development

Create your own specialized agents:

```python
from agentic_finance_workflow.agents import BaseAgent
from typing import Dict, Any

class CustomAnalyzerAgent(BaseAgent):
    """Custom financial analysis agent"""
    
    async def _process(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Your custom analysis logic here
        df = input_data['data']
        
        # Perform analysis
        results = self.custom_analysis(df)
        
        return {
            'analysis_results': results,
            'metadata': {
                'rows_processed': len(df),
                'analysis_type': 'custom'
            }
        }
    
    def custom_analysis(self, df):
        # Implementation details
        pass

# Register your agent
from agentic_finance_workflow.registry import agent_registry
agent_registry.register('CustomAnalyzerAgent', CustomAnalyzerAgent)
```

### Integration with External Services

#### Market Data Providers

```python
# Configure external data sources
MARKET_DATA_PROVIDERS:
  alpha_vantage:
    api_key: "your-api-key"
    rate_limit: 5  # requests per minute
  
  yahoo_finance:
    enabled: true
    timeout: 30
```

#### Notification Services

```python
# Configure alerts and notifications
NOTIFICATIONS:
  email:
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-password"
  
  slack:
    webhook_url: "https://hooks.slack.com/your-webhook"
    channel: "#finance-alerts"
```

## Best Practices

### Data Quality

1. **Always validate your data** before processing
2. **Use appropriate data cleaning strategies** for your use case
3. **Monitor data quality metrics** throughout processing
4. **Keep backups** of original data

### Workflow Design

1. **Start with simple workflows** and gradually add complexity
2. **Use meaningful agent names** and documentation
3. **Configure appropriate timeouts** for long-running processes
4. **Test workflows** with sample data first

### Performance

1. **Use appropriate chunk sizes** for large datasets
2. **Enable parallel processing** when agents are independent
3. **Monitor resource usage** and adjust configuration
4. **Use caching** for frequently accessed data

### Security

1. **Use secure authentication** and authorization
2. **Encrypt sensitive data** at rest and in transit
3. **Regularly update dependencies** for security patches
4. **Monitor access logs** for suspicious activity

## Getting Help

### Documentation
- **API Reference**: `/docs/api.md`
- **Architecture Guide**: `/docs/architecture.md`
- **Developer Guide**: `/docs/development.md`

### Community
- **GitHub Issues**: Report bugs and feature requests
- **Discord**: Join our community chat
- **Stack Overflow**: Tag questions with `agentic-finance-workflow`

### Support
- **Enterprise Support**: Available for enterprise customers
- **Email**: support@agentic-finance.com
- **Documentation**: https://docs.agentic-finance.com

---

*This guide covers the basics of using the Agentic Finance Workflow system. For more advanced topics, refer to the specific documentation sections.*
