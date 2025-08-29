#!/bin/bash

# Enhanced Production Startup Script for Agentic Finance Workflow
set -e

echo "🚀 Starting Agentic Finance Workflow Production Environment..."

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

# Check if Docker is running
if ! docker info &> /dev/null; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data nginx/ssl static

# Set proper permissions
chmod 755 logs data static
if [ -d "nginx/ssl" ]; then
    chmod 700 nginx/ssl
fi

# Check if environment file exists
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Created .env file from .env.example"
    else
        print_warning "No .env.example found. Creating basic .env file..."
        cat > .env << EOF
# Production Environment Variables
ENVIRONMENT=production
LOG_LEVEL=info
API_HOST=0.0.0.0
API_PORT=8001
CORS_ORIGINS=*
EOF
    fi
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose -f docker-compose.production.yml down --remove-orphans 2>/dev/null || true

# Pull latest images
print_status "Pulling latest base images..."
docker-compose -f docker-compose.production.yml pull --ignore-pull-failures

# Build the application
print_status "Building the application..."
docker-compose -f docker-compose.production.yml build --no-cache

# Start the services
print_status "Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check if API is healthy
for i in {1..30}; do
    if curl -f http://localhost:8001/health &> /dev/null; then
        print_success "API service is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "API service failed to become healthy"
        docker-compose -f docker-compose.production.yml logs agentic-finance-api
        exit 1
    fi
    sleep 2
done

# Check if nginx is responding
for i in {1..10}; do
    if curl -f http://localhost:8080/ &> /dev/null; then
        print_success "Nginx service is healthy!"
        break
    fi
    if [ $i -eq 10 ]; then
        print_warning "Nginx service may not be responding correctly"
        docker-compose -f docker-compose.production.yml logs agentic-finance-nginx
    fi
    sleep 2
done

# Display service status
print_status "Service Status:"
docker-compose -f docker-compose.production.yml ps

# Display access information
echo ""
print_success "🎉 Production environment started successfully!"
echo ""
echo "📊 Access Points:"
echo "   Web Interface: http://localhost:8080/"
echo "   API Direct:    http://localhost:8001/"
echo "   API Docs:      http://localhost:8001/api/docs"
echo "   Health Check:  http://localhost:8001/health"
echo ""
echo "📋 Management Commands:"
echo "   View logs:     docker-compose -f docker-compose.production.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.production.yml down"
echo "   Restart:       docker-compose -f docker-compose.production.yml restart"
echo ""
echo "🔧 Monitoring:"
echo "   Container status: docker-compose -f docker-compose.production.yml ps"
echo "   Resource usage:   docker stats"
echo ""

# Optional: Show recent logs
read -p "Would you like to see recent logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Showing recent logs (Ctrl+C to exit)..."
    docker-compose -f docker-compose.production.yml logs -f --tail=50
fi
