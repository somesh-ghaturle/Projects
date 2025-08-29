#!/bin/bash

# Microsoft Stock Trading Platform - Development Startup Script
# This script starts the development environment with simplified services

set -e

echo "🚀 Starting Microsoft Stock Trading Platform (Development Mode)"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="microsoft-stock-trading-dev"
COMPOSE_FILE="docker-compose.dev.yml"

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
check_docker() {
    print_status "Checking Docker status..."
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p database/dev
    mkdir -p ollama/models
    print_success "Directories created"
}

# Start services
start_services() {
    print_status "Starting development services..."
    
    # Start Ollama first
    print_status "Starting Ollama AI service..."
    docker-compose -f $COMPOSE_FILE up -d ollama
    
    # Wait for Ollama to be ready
    print_status "Waiting for Ollama to start..."
    sleep 15
    
    # Start n8n with SQLite
    print_status "Starting n8n with SQLite database..."
    docker-compose -f $COMPOSE_FILE up -d n8n
    
    # Wait for n8n to be ready
    print_status "Waiting for n8n to be ready..."
    sleep 20
    
    print_success "Development services started successfully"
}

# Setup Ollama models
setup_ollama() {
    print_status "Setting up Ollama AI models..."
    
    # Wait a bit more for Ollama to be fully ready
    sleep 10
    
    # Pull required models
    print_status "Downloading AI models (this may take a while)..."
    docker-compose -f $COMPOSE_FILE exec -T ollama ollama pull llama3:latest || print_warning "Failed to pull llama3:latest"
    docker-compose -f $COMPOSE_FILE exec -T ollama ollama pull llama3.2:latest || print_warning "Failed to pull llama3.2:latest"
    
    print_success "Ollama models setup completed"
}

# Health check
health_check() {
    print_status "Performing health checks..."
    
    # Check n8n
    if curl -f http://localhost:5678/healthz >/dev/null 2>&1; then
        print_success "n8n is healthy"
    else
        print_warning "n8n may still be starting up"
    fi
    
    # Check Ollama
    if curl -f http://localhost:11434/api/version >/dev/null 2>&1; then
        print_success "Ollama is healthy"
    else
        print_warning "Ollama may still be starting up"
    fi
}

# Show service information
show_info() {
    echo ""
    echo "🎯 Microsoft Stock Trading Platform - Development Environment"
    echo "==========================================================="
    echo ""
    echo "📊 n8n Workflow Automation:"
    echo "   URL: http://localhost:5678"
    echo "   Database: SQLite (development)"
    echo ""
    echo "🤖 Ollama AI Service:"
    echo "   URL: http://localhost:11434"
    echo "   Models: llama3:latest, llama3.2:latest"
    echo ""
    echo "📁 Development Directories:"
    echo "   Workflows: ./workflows/"
    echo "   Database: ./database/dev/"
    echo "   Logs: ./logs/"
    echo ""
    echo "🛠️  Management Commands:"
    echo "   View logs: docker-compose -f docker-compose.dev.yml logs -f [service]"
    echo "   Stop all: docker-compose -f docker-compose.dev.yml down"
    echo "   Restart: docker-compose -f docker-compose.dev.yml restart [service]"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Access n8n at http://localhost:5678"
    echo "   2. Import workflows from ./workflows/ directory"
    echo "   3. Configure Gmail credentials in workflow"
    echo "   4. Test the stock trading workflow"
    echo ""
    echo "💡 Note: This is a development environment with simplified services"
    echo "   For production deployment, use './start-production.sh' instead"
    echo ""
}

# Main execution
main() {
    echo "Starting Microsoft Stock Trading Platform (Development)..."
    
    check_docker
    create_directories
    start_services
    setup_ollama
    health_check
    show_info
    
    print_success "Development environment is now running!"
    print_status "Press Ctrl+C to view logs, or run 'docker-compose -f docker-compose.dev.yml logs -f' to monitor services"
    
    # Follow logs
    docker-compose -f $COMPOSE_FILE logs -f
}

# Handle interrupts
trap 'echo -e "\n🛑 Shutting down..."; docker-compose -f $COMPOSE_FILE down; exit 0' INT TERM

# Run main function
main "$@"
    echo -n "."
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -ge $timeout ]; then
    echo ""
    echo "❌ Timeout waiting for n8n to start. Check logs:"
    docker-compose logs n8n
    exit 1
fi

echo ""
echo "🎉 n8n Trading Workflow is now running!"
echo ""
echo "📊 Access your workflow at: http://localhost:5678"
echo "👤 Username: $N8N_BASIC_AUTH_USER"
echo "🔑 Password: $N8N_BASIC_AUTH_PASSWORD"
echo ""
echo "📋 Useful commands:"
echo "  • View logs:     docker-compose logs -f n8n"
echo "  • Stop:          docker-compose down"
echo "  • Restart:       docker-compose restart n8n"
echo "  • Shell access:  docker-compose exec n8n sh"
echo ""
echo "📁 To import the workflow:"
echo "  1. Go to http://localhost:5678"
echo "  2. Click on 'Workflows' in the left sidebar"
echo "  3. Click 'Import from file'"
echo "  4. Upload the trading-workflow.json file"
echo ""
echo "🔔 Don't forget to configure your Discord webhook in the workflow!"
echo "=================================================="
