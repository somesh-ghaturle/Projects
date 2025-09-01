#!/bin/bash

# MedAssist AI MCP - Production Health Check Script
# Comprehensive health monitoring for medical AI platform

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check container status
check_containers() {
    print_status "Checking container status..."
    
    containers=("medassist_api_prod" "medassist_nginx_prod" "medassist_redis_prod" "medassist_postgres_prod")
    all_healthy=true
    
    for container in "${containers[@]}"; do
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container.*Up"; then
            print_success "$container is running"
        else
            print_error "$container is not running"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        print_success "All core containers are running"
    else
        print_error "Some containers are not running"
        return 1
    fi
}

# Check API endpoints
check_api_endpoints() {
    print_status "Checking API endpoints..."
    
    # Health endpoint
    if curl -f -s http://localhost:8080/health > /dev/null; then
        print_success "Health endpoint is responding"
    else
        print_error "Health endpoint is not responding"
        return 1
    fi
    
    # Medical agent endpoints
    agents=("diagnostic" "pharmacy" "radiology" "treatment" "emergency" "enterprise")
    
    for agent in "${agents[@]}"; do
        if curl -f -s -X POST http://localhost:8080/$agent \
           -H "Content-Type: application/json" \
           -d '{"query": "test"}' > /dev/null; then
            print_success "$agent agent is responding"
        else
            print_warning "$agent agent may have issues"
        fi
    done
}

# Check database connectivity
check_database() {
    print_status "Checking database connectivity..."
    
    if docker exec medassist_postgres_prod pg_isready -U medassist_user -d medassist_db > /dev/null 2>&1; then
        print_success "PostgreSQL database is accessible"
    else
        print_error "PostgreSQL database is not accessible"
        return 1
    fi
}

# Check Redis connectivity
check_redis() {
    print_status "Checking Redis connectivity..."
    
    if docker exec medassist_redis_prod redis-cli ping > /dev/null 2>&1; then
        print_success "Redis is accessible"
    else
        print_error "Redis is not accessible"
        return 1
    fi
}

# Check resource usage
check_resources() {
    print_status "Checking resource usage..."
    
    # Memory usage
    memory_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}" | grep medassist)
    if [ -n "$memory_usage" ]; then
        print_status "Memory usage:"
        echo "$memory_usage"
    fi
    
    # CPU usage
    cpu_usage=$(docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}" | grep medassist)
    if [ -n "$cpu_usage" ]; then
        print_status "CPU usage:"
        echo "$cpu_usage"
    fi
}

# Check logs for errors
check_logs() {
    print_status "Checking recent logs for errors..."
    
    # Check API logs for errors in last 10 lines
    api_errors=$(docker logs --tail 10 medassist_api_prod 2>&1 | grep -i "error\|exception\|failed" || true)
    
    if [ -n "$api_errors" ]; then
        print_warning "Recent errors found in API logs:"
        echo "$api_errors"
    else
        print_success "No recent errors in API logs"
    fi
}

# Generate health report
generate_report() {
    echo ""
    echo "🏥 ==============================================="
    echo "🏥 MedAssist AI MCP Health Check Report"
    echo "🏥 ==============================================="
    echo "   Timestamp: $(date)"
    echo ""
    
    # Overall status
    if check_containers && check_database && check_redis; then
        print_success "🟢 System Status: HEALTHY"
        echo "   All core services are operational"
    else
        print_error "🔴 System Status: UNHEALTHY"
        echo "   Some services require attention"
    fi
    
    echo ""
    echo "🔗 Service URLs:"
    echo "   Medical Interface: http://localhost:8080"
    echo "   Grafana Dashboard: http://localhost:3000"
    echo "   Prometheus Metrics: http://localhost:9090"
    echo ""
    
    # Quick troubleshooting
    echo "🛠️ Troubleshooting:"
    echo "   View all logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "   Restart services: docker-compose -f docker-compose.production.yml restart"
    echo "   View detailed status: docker-compose -f docker-compose.production.yml ps"
}

# Main health check
main() {
    echo "🏥 MedAssist AI MCP - Health Check"
    echo "================================="
    
    check_containers
    check_api_endpoints
    check_database
    check_redis
    check_resources
    check_logs
    generate_report
}

main "$@"
