#!/bin/bash

# Microsoft Stock Trading Platform - Health Check Script
# This script checks the health of all running services

set -e

echo "🏥 Microsoft Stock Trading Platform - Health Check"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running"
    exit 1
fi

print_success "Docker is running"

# Move to the script directory's parent
cd "$(dirname "$0")/.."

# Determine which compose file is being used
COMPOSE_FILE=""
if [ -f "docker-compose.yml" ] && docker-compose -f docker-compose.yml ps | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.yml"
    print_status "Using production configuration (docker-compose.yml)"
elif [ -f "docker-compose.dev.yml" ] && docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.dev.yml"
    print_status "Using development configuration (docker-compose.dev.yml)"
else
    print_error "No running services found"
    exit 1
fi

echo ""
echo "� Checking Service Health:"
echo "=========================="

# Check PostgreSQL (production only)
if [ "$COMPOSE_FILE" = "docker-compose.yml" ]; then
    print_status "Checking PostgreSQL..."
    if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U n8n >/dev/null 2>&1; then
        print_success "PostgreSQL is healthy"
        
        # Get database info
        DB_SIZE=$(docker-compose -f $COMPOSE_FILE exec -T postgres psql -U n8n -d n8n -t -c "SELECT pg_size_pretty(pg_database_size('n8n'));" 2>/dev/null | xargs || echo "Unknown")
        echo "   Database size: $DB_SIZE"
    else
        print_error "PostgreSQL is not responding"
    fi
    
    # Check Redis
    print_status "Checking Redis..."
    if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
        print_success "Redis is healthy"
        
        # Get Redis info
        REDIS_MEMORY=$(docker-compose -f $COMPOSE_FILE exec -T redis redis-cli info memory 2>/dev/null | grep used_memory_human | cut -d: -f2 | tr -d '\r' || echo "Unknown")
        echo "   Memory usage: $REDIS_MEMORY"
    else
        print_error "Redis is not responding"
    fi
fi

# Check n8n
print_status "Checking n8n..."
if curl -f -s http://localhost:5678/healthz >/dev/null 2>&1; then
    print_success "n8n is healthy"
    
    # Get n8n version
    N8N_VERSION=$(curl -s http://localhost:5678/types/nodes.json 2>/dev/null | jq -r '.n8n.version' 2>/dev/null || echo "Unknown")
    echo "   Version: $N8N_VERSION"
    
    # Check if n8n can connect to database
    if curl -f -s http://localhost:5678/rest/login >/dev/null 2>&1; then
        print_success "n8n database connection is working"
    else
        print_warning "n8n database connection may have issues"
    fi
else
    print_error "n8n is not responding"
fi

# Check Ollama
print_status "Checking Ollama..."
if curl -f -s http://localhost:11434/api/version >/dev/null 2>&1; then
    print_success "Ollama is healthy"
    
    # Get Ollama version
    OLLAMA_VERSION=$(curl -s http://localhost:11434/api/version 2>/dev/null | jq -r '.version' 2>/dev/null || echo "Unknown")
    echo "   Version: $OLLAMA_VERSION"
    
    # List available models
    print_status "Available Ollama models:"
    MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | jq -r '.models[].name' 2>/dev/null | sed 's/^/   • /' || echo "   Unable to fetch models")
    echo "$MODELS"
else
    print_error "Ollama is not responding"
fi

# Check Nginx (if running)
if docker-compose -f $COMPOSE_FILE ps | grep -q nginx; then
    print_status "Checking Nginx..."
    if curl -f -s http://localhost:80/health >/dev/null 2>&1; then
        print_success "Nginx is healthy"
    else
        print_warning "Nginx health check failed"
    fi
fi

echo ""
echo "📊 Resource Usage:"
echo "=================="

# Docker stats
print_status "Container resource usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker-compose -f $COMPOSE_FILE ps -q) 2>/dev/null || print_warning "Unable to get resource stats"

echo ""
echo "🔗 Service URLs:"
echo "==============="

echo "• n8n:    http://localhost:5678"
echo "• Ollama: http://localhost:11434"

if [ "$COMPOSE_FILE" = "docker-compose.yml" ]; then
    echo "• PostgreSQL: localhost:5432"
    echo "• Redis: localhost:6379"
fi

if docker-compose -f $COMPOSE_FILE ps | grep -q nginx; then
    echo "• Nginx: http://localhost:80"
fi

echo ""
echo "💡 Tips:"
echo "======="
echo "• View logs: docker-compose -f $COMPOSE_FILE logs -f [service]"
echo "• Restart service: docker-compose -f $COMPOSE_FILE restart [service]"
echo "• Stop all: docker-compose -f $COMPOSE_FILE down"

if [ "$COMPOSE_FILE" = "docker-compose.yml" ]; then
    echo "• Backup database: docker-compose -f $COMPOSE_FILE exec postgres pg_dump -U n8n n8n > backup.sql"
fi

echo ""
print_success "Health check completed!"
