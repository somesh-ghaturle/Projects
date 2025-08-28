#!/bin/bash
# Production deployment script for AgenTech Research Hub

set -e

echo "🚀 Starting AgenTech Research Hub Production Deployment"

# Configuration
ENVIRONMENT=${1:-production}
COMPOSE_FILE="docker-compose.yml"

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
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment file exists
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f ".env.${ENVIRONMENT}" ]; then
        print_error "Environment file .env.${ENVIRONMENT} not found!"
        print_warning "Please create .env.${ENVIRONMENT} based on .env.example"
        exit 1
    fi
    
    if [ ! -f "${COMPOSE_FILE}" ]; then
        print_error "Docker compose file ${COMPOSE_FILE} not found!"
        exit 1
    fi
    
    print_success "Environment configuration found"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed!"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running!"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create necessary directories
setup_directories() {
    print_status "Setting up directories..."
    
    mkdir -p data/{logs,cache,outputs,processed,raw,vector_db}
    mkdir -p logs/{nginx,app}
    mkdir -p nginx/ssl
    
    # Set proper permissions
    chmod 755 data logs
    chmod -R 755 data/* logs/*
    
    print_success "Directories created"
}

# Generate SSL certificates (self-signed for development)
setup_ssl() {
    if [ "${ENVIRONMENT}" = "production" ]; then
        print_status "Setting up SSL certificates..."
        
        if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
            print_warning "SSL certificates not found. Generating self-signed certificates..."
            print_warning "For production, replace with proper SSL certificates!"
            
            openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout nginx/ssl/key.pem \
                -out nginx/ssl/cert.pem \
                -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
            
            print_success "Self-signed SSL certificates generated"
        else
            print_success "SSL certificates found"
        fi
    fi
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Stop existing services
    docker-compose -f "${COMPOSE_FILE}" down 2>/dev/null || true
    
    # Build images
    print_status "Building Docker images..."
    docker-compose -f "${COMPOSE_FILE}" build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f "${COMPOSE_FILE}" up -d
    
    print_success "Services started"
}

# Wait for services to be healthy
wait_for_services() {
    print_status "Waiting for services to be healthy..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout 60 bash -c 'until docker-compose -f "${COMPOSE_FILE}" exec -T postgres pg_isready -U agentech; do sleep 2; done'
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout 60 bash -c 'until docker-compose -f "${COMPOSE_FILE}" exec -T redis redis-cli ping | grep PONG; do sleep 2; done'
    
    # Wait for API
    print_status "Waiting for API..."
    timeout 120 bash -c 'until curl -f http://localhost:8000/health; do sleep 5; done'
    
    print_success "All services are healthy"
}

# Run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # API health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_success "API health check passed"
    else
        print_error "API health check failed"
        return 1
    fi
    
    # Web UI check
    if curl -f http://localhost:80 > /dev/null 2>&1; then
        print_success "Web UI health check passed"
    else
        print_error "Web UI health check failed"
        return 1
    fi
    
    # Database check
    if docker-compose -f "${COMPOSE_FILE}" exec -T postgres pg_isready -U agentech > /dev/null 2>&1; then
        print_success "Database health check passed"
    else
        print_error "Database health check failed"
        return 1
    fi
    
    print_success "All health checks passed"
}

# Show deployment information
show_deployment_info() {
    print_success "🎉 AgenTech Research Hub deployed successfully!"
    echo ""
    echo "📍 Access Points:"
    echo "   Web UI:      http://localhost:80"
    echo "   API:         http://localhost:8000"
    echo "   API Docs:    http://localhost:8000/docs"
    echo "   Health:      http://localhost:8000/health"
    echo "   Grafana:     http://localhost:3001 (admin/admin123)"
    echo "   Prometheus:  http://localhost:9090"
    echo ""
    echo "🔧 Management Commands:"
    echo "   View logs:   docker-compose -f ${COMPOSE_FILE} logs -f"
    echo "   Stop:        docker-compose -f ${COMPOSE_FILE} down"
    echo "   Restart:     docker-compose -f ${COMPOSE_FILE} restart"
    echo ""
    echo "📊 Monitoring:"
    echo "   Service status: docker-compose -f ${COMPOSE_FILE} ps"
    echo "   Resource usage: docker stats"
    echo ""
}

# Main deployment flow
main() {
    print_status "Starting deployment for environment: ${ENVIRONMENT}"
    
    check_prerequisites
    check_environment
    setup_directories
    setup_ssl
    deploy_services
    wait_for_services
    run_health_checks
    show_deployment_info
    
    print_success "Deployment completed successfully! 🚀"
}

# Handle script interruption
trap 'print_error "Deployment interrupted!"; exit 1' INT TERM

# Run main function
main "$@"
