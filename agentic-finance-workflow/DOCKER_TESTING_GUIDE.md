# Complete Docker Testing Guide

This guide provides comprehensive instructions for testing the entire Docker setup including Dockerfile, docker-compose.yml, API endpoints, workflows, and all services.

## 🚀 Quick Start Testing

### Prerequisites
```bash
# Make sure Docker is running
docker --version
docker-compose --version

# Install Python testing dependencies
pip3 install requests psycopg2-binary redis
```

### Run All Tests
```bash
# Complete test suite (recommended)
./test_complete_suite.sh

# Or run individual test suites:
./test_docker_complete.sh          # Basic Docker infrastructure
python3 test_docker_complete.py    # Detailed infrastructure tests
python3 test_workflows_docker.py   # Workflow-specific tests
```

## 📋 Test Categories

### 1. Docker Infrastructure Tests
- ✅ Container status and health checks
- ✅ Service networking (postgres, redis, api)
- ✅ Volume persistence
- ✅ Docker Compose configuration validation
- ✅ Dockerfile build testing

### 2. Database & Cache Tests
- ✅ PostgreSQL connection and database existence
- ✅ Redis connection and basic operations
- ✅ Container-to-container networking

### 3. API Endpoint Tests
- ✅ Health check endpoint (`/health`)
- ✅ Root endpoint (`/`)
- ✅ Data cleaning endpoint (`/api/v1/clean`)
- ✅ Workflow execution endpoint (`/api/v1/workflow/execute`)
- ✅ Metrics endpoint (`/api/v1/metrics`)

### 4. Workflow Tests
- 🔄 Data cleaning workflows
- 🔄 Analysis workflows (risk, technical, portfolio)
- 🔄 Agent interactions
- 🔄 Error handling scenarios

### 5. Performance Tests
- ✅ Memory usage monitoring
- ✅ Concurrent request handling
- ✅ Log analysis for errors

## 🛠️ Manual Testing Commands

### Container Status
```bash
# Check running containers
docker ps

# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View container logs
docker logs agentic-finance-workflow-api-1
docker logs agentic-finance-workflow-postgres-1
docker logs agentic-finance-workflow-redis-1
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# API documentation
open http://localhost:8000/docs

# Data cleaning test
curl -X POST http://localhost:8000/api/v1/clean \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "timestamp": "2023-01-01T00:00:00",
        "symbol": "AAPL",
        "open": 150.0,
        "high": 155.0,
        "low": 149.0,
        "close": 152.0,
        "volume": 1000000
      }
    ]
  }'

# Workflow execution test
curl -X POST http://localhost:8000/api/v1/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_definition": {
      "workflow_id": "test-workflow",
      "name": "Test Workflow",
      "steps": [
        {
          "step_id": "clean",
          "agent_type": "CLEANER"
        }
      ]
    },
    "input_parameters": {
      "data": [
        {
          "timestamp": "2023-01-01T00:00:00",
          "symbol": "AAPL",
          "open": 150.0,
          "high": 155.0,
          "low": 149.0,
          "close": 152.0,
          "volume": 1000000
        }
      ]
    }
  }'
```

### Database Testing
```bash
# PostgreSQL connection test
docker exec agentic-finance-workflow-postgres-1 pg_isready -h localhost -p 5432

# List databases
docker exec agentic-finance-workflow-postgres-1 psql -U postgres -l

# Connect to database
docker exec -it agentic-finance-workflow-postgres-1 psql -U postgres -d agentic_finance_dev

# Redis connection test
docker exec agentic-finance-workflow-redis-1 redis-cli ping

# Redis operations
docker exec agentic-finance-workflow-redis-1 redis-cli set test_key test_value
docker exec agentic-finance-workflow-redis-1 redis-cli get test_key
```

### Network Testing
```bash
# Test API to PostgreSQL connectivity
docker exec agentic-finance-workflow-api-1 python -c "
import socket
s = socket.socket()
s.settimeout(1)
s.connect(('postgres', 5432))
print('Connected to postgres:5432')
s.close()
"

# Test API to Redis connectivity
docker exec agentic-finance-workflow-api-1 python -c "
import socket
s = socket.socket()
s.settimeout(1)
s.connect(('redis', 6379))
print('Connected to redis:6379')
s.close()
"
```

### Performance Monitoring
```bash
# Container resource usage
docker stats

# Container memory and CPU usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Disk usage
docker system df
```

## 🔧 Troubleshooting

### Common Issues

1. **Containers not starting**
   ```bash
   # Check container logs
   docker-compose logs
   
   # Restart services
   docker-compose down
   docker-compose up -d
   ```

2. **Database connection failures**
   ```bash
   # Check if PostgreSQL is ready
   docker exec agentic-finance-workflow-postgres-1 pg_isready
   
   # Verify environment variables
   docker exec agentic-finance-workflow-api-1 env | grep -E "(POSTGRES|DATABASE)"
   ```

3. **API endpoints returning 404**
   ```bash
   # Check API server logs
   docker logs agentic-finance-workflow-api-1
   
   # Verify API is running on correct port
   docker ps | grep api
   ```

4. **Network connectivity issues**
   ```bash
   # Check Docker networks
   docker network ls
   
   # Inspect network configuration
   docker network inspect agentic-finance-workflow_default
   ```

### Log Analysis
```bash
# Search for errors in logs
docker logs agentic-finance-workflow-api-1 2>&1 | grep -i error

# Get recent logs
docker logs agentic-finance-workflow-api-1 --tail 50

# Follow logs in real-time
docker logs agentic-finance-workflow-api-1 -f
```

## 📊 Test Results

After running tests, check these files for detailed results:
- `docker_test_results.json` - Basic infrastructure test results
- `workflow_test_results.json` - Workflow-specific test results

## 🎯 Success Criteria

✅ **Fully Successful Setup:**
- All containers running and healthy
- Database and Redis connections working
- Basic API endpoints responding (health, root, metrics)
- Data cleaning endpoint functional
- Basic workflow execution working
- No serious errors in logs

🔄 **Partially Successful Setup:**
- Core infrastructure working
- Some advanced workflow endpoints not yet implemented
- Performance acceptable under load

❌ **Failed Setup:**
- Containers not starting
- Database connection failures
- API completely unresponsive

## 🚀 Next Steps

After successful testing:
1. Implement additional workflow endpoints
2. Add comprehensive error handling
3. Set up monitoring and alerting
4. Configure production environment variables
5. Set up CI/CD pipelines

## 📝 Notes

- The current setup focuses on core functionality
- Advanced workflow features are partially implemented
- Environment is configured for development/testing
- Production deployment requires additional security considerations
