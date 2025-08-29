#!/bin/bash

# Production Health Monitor for Agentic Finance Workflow
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local url=$2
    local timeout=${3:-10}
    
    if curl -f --max-time $timeout "$url" &> /dev/null; then
        print_success "$service_name is healthy"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Function to check container status
check_container_status() {
    local container_name=$1
    
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$container_name.*Up"; then
        local status=$(docker ps --format "{{.Status}}" --filter "name=$container_name")
        print_success "$container_name: $status"
        return 0
    else
        print_error "$container_name is not running"
        return 1
    fi
}

# Function to check resource usage
check_resource_usage() {
    local container_name=$1
    
    if docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -q "$container_name"; then
        local stats=$(docker stats --no-stream --format "{{.CPUPerc}}\t{{.MemUsage}}" --filter "name=$container_name")
        print_status "$container_name resources: CPU: $(echo $stats | cut -f1) | Memory: $(echo $stats | cut -f2)"
    fi
}

echo "🏥 Agentic Finance Workflow - Health Check"
echo "========================================"
echo ""

# Check Docker
print_status "Checking Docker daemon..."
if docker info &> /dev/null; then
    print_success "Docker daemon is running"
else
    print_error "Docker daemon is not running"
    exit 1
fi

echo ""
print_status "Checking container status..."

# Check containers
api_healthy=true
nginx_healthy=true

if ! check_container_status "agentic-finance-production"; then
    api_healthy=false
fi

if ! check_container_status "agentic-finance-nginx"; then
    nginx_healthy=false
fi

echo ""
print_status "Checking service endpoints..."

# Check API health
if ! check_service_health "API Service" "http://localhost:8001/health" 15; then
    api_healthy=false
fi

# Check web interface
if ! check_service_health "Web Interface" "http://localhost:8080/" 15; then
    nginx_healthy=false
fi

# Check API documentation
if ! check_service_health "API Documentation" "http://localhost:8001/api/docs" 10; then
    print_warning "API documentation may not be accessible"
fi

echo ""
print_status "Checking resource usage..."
check_resource_usage "agentic-finance-production"
check_resource_usage "agentic-finance-nginx"

echo ""
print_status "Checking disk space..."
df_output=$(df -h .)
available_space=$(echo "$df_output" | awk 'NR==2 {print $4}')
used_percent=$(echo "$df_output" | awk 'NR==2 {print $5}' | sed 's/%//')

if [ "$used_percent" -lt 80 ]; then
    print_success "Disk space: $available_space available (${used_percent}% used)"
elif [ "$used_percent" -lt 90 ]; then
    print_warning "Disk space: $available_space available (${used_percent}% used)"
else
    print_error "Low disk space: $available_space available (${used_percent}% used)"
fi

echo ""
print_status "Checking log file sizes..."
if [ -d "logs" ]; then
    log_size=$(du -sh logs 2>/dev/null | cut -f1)
    print_status "Log directory size: $log_size"
else
    print_warning "Log directory not found"
fi

echo ""
print_status "Recent container logs (last 5 lines)..."
echo "API Logs:"
docker logs --tail 5 agentic-finance-production 2>/dev/null || print_warning "Could not retrieve API logs"
echo ""
echo "Nginx Logs:"
docker logs --tail 5 agentic-finance-nginx 2>/dev/null || print_warning "Could not retrieve Nginx logs"

echo ""
echo "========================================"

# Overall health assessment
if [ "$api_healthy" = true ] && [ "$nginx_healthy" = true ]; then
    print_success "🎉 All services are healthy!"
    echo ""
    echo "🌐 Access Points:"
    echo "   Web Interface: http://localhost:8080/"
    echo "   API Endpoint:  http://localhost:8001/"
    echo "   API Docs:      http://localhost:8001/api/docs"
    exit 0
else
    print_error "❌ Some services are not healthy!"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   View logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "   Restart:   docker-compose -f docker-compose.production.yml restart"
    echo "   Rebuild:   docker-compose -f docker-compose.production.yml up -d --build"
    exit 1
fi
