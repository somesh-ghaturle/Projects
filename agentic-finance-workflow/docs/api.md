# Agentic Finance Workflow - API Documentation

## Overview

The Agentic Finance Workflow provides a comprehensive GraphQL API for financial data processing and analysis. This document covers all available queries, mutations, subscriptions, and their usage.

## GraphQL Endpoint

- **Development**: `http://localhost:8000/graphql`
- **Production**: `https://api.agentic-finance.com/graphql`
- **GraphQL Playground**: Available at the same endpoints for interactive exploration

## Authentication

All API requests require authentication using JWT tokens:

```bash
# Include in headers
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```graphql
mutation Login {
  login(email: "user@example.com", password: "password") {
    token
    user {
      id
      email
      role
    }
  }
}
```

## Core Types

### AgentResult

```graphql
type AgentResult {
  id: ID!
  agentType: String!
  status: AgentStatus!
  output: JSON
  error: String
  metrics: AgentMetrics!
  startTime: DateTime!
  endTime: DateTime
  executionId: String!
}

enum AgentStatus {
  PENDING
  RUNNING
  COMPLETED
  FAILED
  CANCELLED
}
```

### WorkflowExecution

```graphql
type WorkflowExecution {
  id: ID!
  workflowId: String!
  status: WorkflowStatus!
  inputData: JSON!
  agentResults: [AgentResult!]!
  startTime: DateTime!
  endTime: DateTime
  metadata: JSON
}

enum WorkflowStatus {
  INITIALIZED
  RUNNING
  COMPLETED
  FAILED
  CANCELLED
}
```

### FinancialData

```graphql
type StockPrice {
  symbol: String!
  timestamp: DateTime!
  open: Float!
  high: Float!
  low: Float!
  close: Float!
  volume: Int!
  adjustedClose: Float
}

type Portfolio {
  id: ID!
  name: String!
  totalValue: Float!
  positions: [Position!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Position {
  symbol: String!
  quantity: Float!
  averagePrice: Float!
  currentPrice: Float!
  marketValue: Float!
  unrealizedPnl: Float!
}
```

## Queries

### Agent Operations

#### Get Agent Status

```graphql
query GetAgentStatus($agentId: ID!) {
  agent(id: $agentId) {
    id
    type
    status
    healthStatus {
      isHealthy
      lastCheck
      metrics {
        cpu
        memory
        diskUsage
      }
    }
  }
}
```

#### List Available Agents

```graphql
query ListAgents {
  agents {
    id
    type
    description
    capabilities
    status
    configuration {
      parameters
      requirements
    }
  }
}
```

### Workflow Operations

#### Get Workflow Execution

```graphql
query GetWorkflowExecution($executionId: ID!) {
  workflowExecution(id: $executionId) {
    id
    workflowId
    status
    inputData
    agentResults {
      id
      agentType
      status
      output
      metrics {
        executionTime
        memoryUsage
        errorCount
      }
    }
    startTime
    endTime
  }
}
```

#### List Workflow Templates

```graphql
query ListWorkflowTemplates {
  workflowTemplates {
    id
    name
    description
    agents {
      type
      dependencies
      configuration
    }
    parameters {
      name
      type
      required
      defaultValue
    }
  }
}
```

### Financial Data Queries

#### Get Stock Prices

```graphql
query GetStockPrices(
  $symbols: [String!]!
  $startDate: DateTime!
  $endDate: DateTime!
  $interval: String = "1d"
) {
  stockPrices(
    symbols: $symbols
    startDate: $startDate
    endDate: $endDate
    interval: $interval
  ) {
    symbol
    timestamp
    open
    high
    low
    close
    volume
    adjustedClose
  }
}
```

#### Get Portfolio Performance

```graphql
query GetPortfolioPerformance($portfolioId: ID!) {
  portfolio(id: $portfolioId) {
    id
    name
    totalValue
    positions {
      symbol
      quantity
      currentPrice
      marketValue
      unrealizedPnl
    }
    performance {
      totalReturn
      dailyReturn
      sharpeRatio
      maxDrawdown
      volatility
    }
  }
}
```

### Analysis Results

#### Get Technical Analysis

```graphql
query GetTechnicalAnalysis(
  $symbol: String!
  $indicators: [String!]!
  $period: Int = 20
) {
  technicalAnalysis(
    symbol: $symbol
    indicators: $indicators
    period: $period
  ) {
    symbol
    timestamp
    indicators {
      name
      value
      signal
    }
    signals {
      type
      strength
      recommendation
    }
  }
}
```

#### Get Risk Metrics

```graphql
query GetRiskMetrics($portfolioId: ID!) {
  riskMetrics(portfolioId: $portfolioId) {
    portfolioId
    calculationDate
    var95
    var99
    expectedShortfall
    beta
    alpha
    sharpeRatio
    sortinoRatio
    maxDrawdown
    correlationMatrix
  }
}
```

## Mutations

### Agent Management

#### Execute Agent

```graphql
mutation ExecuteAgent($input: AgentExecutionInput!) {
  executeAgent(input: $input) {
    id
    agentType
    status
    executionId
    startTime
  }
}

input AgentExecutionInput {
  agentType: String!
  inputData: JSON!
  configuration: JSON
  metadata: JSON
}
```

#### Stop Agent Execution

```graphql
mutation StopAgent($executionId: ID!) {
  stopAgent(executionId: $executionId) {
    success
    message
  }
}
```

### Workflow Management

#### Start Workflow

```graphql
mutation StartWorkflow($input: WorkflowExecutionInput!) {
  startWorkflow(input: $input) {
    id
    workflowId
    status
    startTime
    estimatedDuration
  }
}

input WorkflowExecutionInput {
  workflowId: String!
  inputData: JSON!
  parameters: JSON
  priority: Int = 5
  timeout: Int = 3600
}
```

#### Cancel Workflow

```graphql
mutation CancelWorkflow($executionId: ID!) {
  cancelWorkflow(executionId: $executionId) {
    success
    message
    finalStatus
  }
}
```

### Data Management

#### Upload Financial Data

```graphql
mutation UploadFinancialData($input: FinancialDataUploadInput!) {
  uploadFinancialData(input: $input) {
    uploadId
    status
    recordsProcessed
    errors {
      row
      column
      message
    }
  }
}

input FinancialDataUploadInput {
  dataType: String!
  format: String!
  data: String! # Base64 encoded or JSON string
  metadata: JSON
}
```

#### Create Portfolio

```graphql
mutation CreatePortfolio($input: PortfolioInput!) {
  createPortfolio(input: $input) {
    id
    name
    totalValue
    positions {
      symbol
      quantity
      averagePrice
    }
  }
}

input PortfolioInput {
  name: String!
  description: String
  positions: [PositionInput!]!
}

input PositionInput {
  symbol: String!
  quantity: Float!
  averagePrice: Float!
}
```

### Configuration Management

#### Update Agent Configuration

```graphql
mutation UpdateAgentConfiguration($input: AgentConfigurationInput!) {
  updateAgentConfiguration(input: $input) {
    success
    message
    configuration
  }
}

input AgentConfigurationInput {
  agentType: String!
  parameters: JSON!
  environment: String = "production"
}
```

## Subscriptions

### Real-time Updates

#### Agent Status Updates

```graphql
subscription AgentStatusUpdates($agentTypes: [String!]) {
  agentStatusUpdates(agentTypes: $agentTypes) {
    agentId
    agentType
    status
    metrics {
      executionTime
      memoryUsage
      errorCount
    }
    timestamp
  }
}
```

#### Workflow Progress

```graphql
subscription WorkflowProgress($executionId: ID!) {
  workflowProgress(executionId: $executionId) {
    executionId
    status
    completedSteps
    totalSteps
    currentAgent
    estimatedTimeRemaining
    agentResults {
      agentType
      status
      completionPercentage
    }
  }
}
```

#### Market Data Updates

```graphql
subscription MarketDataUpdates($symbols: [String!]!) {
  marketDataUpdates(symbols: $symbols) {
    symbol
    price
    change
    changePercent
    volume
    timestamp
  }
}
```

#### System Alerts

```graphql
subscription SystemAlerts($severity: AlertSeverity) {
  systemAlerts(severity: $severity) {
    id
    type
    severity
    message
    source
    timestamp
    metadata
  }
}

enum AlertSeverity {
  INFO
  WARNING
  ERROR
  CRITICAL
}
```

## Error Handling

### Standard Error Format

```json
{
  "errors": [
    {
      "message": "Agent execution failed",
      "locations": [{"line": 2, "column": 3}],
      "path": ["executeAgent"],
      "extensions": {
        "code": "AGENT_EXECUTION_ERROR",
        "agentType": "DataCleanerAgent",
        "executionId": "exec_123456",
        "details": {
          "step": "data_validation",
          "reason": "Invalid data format"
        }
      }
    }
  ]
}
```

### Common Error Codes

- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Insufficient permissions
- `AGENT_NOT_FOUND`: Specified agent doesn't exist
- `WORKFLOW_NOT_FOUND`: Specified workflow doesn't exist
- `AGENT_EXECUTION_ERROR`: Agent execution failed
- `WORKFLOW_EXECUTION_ERROR`: Workflow execution failed
- `INVALID_INPUT`: Input validation failed
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Unexpected server error

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Authenticated Users**: 1000 requests per hour
- **Premium Users**: 5000 requests per hour
- **Enterprise Users**: 20000 requests per hour

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

List queries support cursor-based pagination:

```graphql
query ListWorkflowExecutions(
  $first: Int = 20
  $after: String
  $filter: WorkflowExecutionFilter
) {
  workflowExecutions(first: $first, after: $after, filter: $filter) {
    edges {
      node {
        id
        workflowId
        status
      }
      cursor
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
    totalCount
  }
}
```

## Example Usage

### Complete Workflow Example

```javascript
// 1. Start a workflow
const startWorkflowMutation = `
  mutation StartWorkflow($input: WorkflowExecutionInput!) {
    startWorkflow(input: $input) {
      id
      status
      startTime
    }
  }
`;

const workflowInput = {
  workflowId: "financial-analysis-pipeline",
  inputData: {
    symbol: "AAPL",
    startDate: "2024-01-01",
    endDate: "2024-12-31"
  }
};

// 2. Subscribe to progress updates
const progressSubscription = `
  subscription WorkflowProgress($executionId: ID!) {
    workflowProgress(executionId: $executionId) {
      status
      completedSteps
      totalSteps
      currentAgent
    }
  }
`;

// 3. Query results when complete
const resultsQuery = `
  query GetWorkflowResults($executionId: ID!) {
    workflowExecution(id: $executionId) {
      status
      agentResults {
        agentType
        output
        metrics {
          executionTime
        }
      }
    }
  }
`;
```

This API provides comprehensive access to all financial data processing capabilities with real-time updates and detailed monitoring.
