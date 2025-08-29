#!/bin/bash

# Microsoft Stock Trading Platform - Production Startup Script
# This script starts the complete production environment with all services

set -e

echo "🚀 Starting Microsoft Stock Trading Platform (Production Mode)"
echo "============================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="microsoft-stock-trading"
COMPOSE_FILE="docker-compose.yml"

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

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs backup/postgres backup/n8n
    mkdir -p ollama/models
    mkdir -p database/data
    print_success "Directories created"
}

# Set proper permissions
set_permissions() {
    print_status "Setting proper permissions..."
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod 755 database/ ollama/ logs/ backup/
    print_success "Permissions set"
}

# Check for environment file
check_environment() {
    print_status "Checking environment configuration..."
    if [ ! -f ".env" ]; then
        print_warning "No .env file found. Creating default configuration..."
        cat > .env << 'EOF'
# Database Configuration
POSTGRES_DB=n8n
POSTGRES_USER=n8n
POSTGRES_PASSWORD=n8n_secure_password_2024
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=n8n_secure_password_2024

# n8n Configuration
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://localhost:5678/

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_secure_password_2024

# Ollama Configuration
OLLAMA_HOST=ollama
OLLAMA_PORT=11434

# Email Configuration (Gmail)
GMAIL_USER=someshghaturle@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here

# Timezone
TZ=America/New_York

# Execution Mode
EXECUTIONS_MODE=queue
QUEUE_BULL_REDIS_HOST=redis
QUEUE_BULL_REDIS_PORT=6379
QUEUE_BULL_REDIS_PASSWORD=redis_secure_password_2024
EOF
        print_warning "Please update the .env file with your actual credentials before proceeding!"
        print_warning "Especially update GMAIL_APP_PASSWORD with your actual Gmail app password."
        read -p "Press Enter to continue once you've updated the .env file..."
    fi
    print_success "Environment configuration ready"
}

# Pull latest images
pull_images() {
    print_status "Pulling latest Docker images..."
    docker-compose -f $COMPOSE_FILE pull
    print_success "Images pulled successfully"
}

# Start services in order
start_services() {
    print_status "Starting services..."
    
    # Start infrastructure services first
    print_status "Starting infrastructure services (PostgreSQL, Redis)..."
    docker-compose -f $COMPOSE_FILE up -d postgres redis
    
    # Wait for database to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Start Ollama
    print_status "Starting Ollama AI service..."
    docker-compose -f $COMPOSE_FILE up -d ollama
    
    # Wait for Ollama to be ready
    print_status "Waiting for Ollama to start..."
    sleep 15
    
    # Start n8n
    print_status "Starting n8n workflow automation..."
    docker-compose -f $COMPOSE_FILE up -d n8n
    
    # Wait for n8n to be ready
    print_status "Waiting for n8n to be ready..."
    sleep 20
    
    # Start nginx (if enabled)
    if docker-compose -f $COMPOSE_FILE config --services | grep -q nginx; then
        print_status "Starting Nginx reverse proxy..."
        docker-compose -f $COMPOSE_FILE up -d nginx
    fi
    
    print_success "All services started successfully"
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
    docker-compose -f $COMPOSE_FILE exec -T ollama ollama pull codellama:latest || print_warning "Failed to pull codellama:latest"
    
    print_success "Ollama models setup completed"
}

# Import workflows
import_workflows() {
    print_status "Importing trading workflows..."
    
    # Wait for n8n to be fully ready
    sleep 10
    
    # The workflow will need to be imported manually through the n8n UI
    # or via API calls once n8n is fully operational
    print_warning "Workflows need to be imported manually through the n8n interface"
    print_warning "Access n8n at: http://localhost:5678"
    print_warning "Import the workflow files from the workflows/ directory"
}

# Health check
health_check() {
    print_status "Performing health checks..."
    
    # Check PostgreSQL
    if docker-compose -f $COMPOSE_FILE exec -T postgres pg_isready -U n8n >/dev/null 2>&1; then
        print_success "PostgreSQL is healthy"
    else
        print_error "PostgreSQL is not responding"
    fi
    
    # Check Redis
    if docker-compose -f $COMPOSE_FILE exec -T redis redis-cli ping | grep -q PONG; then
        print_success "Redis is healthy"
    else
        print_error "Redis is not responding"
    fi
    
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
    echo "� Microsoft Stock Trading Platform - Service Information"
    echo "========================================================"
    echo ""
    echo "📊 n8n Workflow Automation:"
    echo "   URL: http://localhost:5678"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""
    echo "🤖 Ollama AI Service:"
    echo "   URL: http://localhost:11434"
    echo "   Models: llama3:latest, llama3.2:latest, codellama:latest"
    echo ""
    echo "🗄️  PostgreSQL Database:"
    echo "   Host: localhost:5432"
    echo "   Database: n8n"
    echo "   Username: n8n"
    echo ""
    echo "🔄 Redis Queue:"
    echo "   Host: localhost:6379"
    echo ""
    echo "� Important Directories:"
    echo "   Workflows: ./workflows/"
    echo "   Database Data: ./database/data/"
    echo "   Logs: ./logs/"
    echo "   Backups: ./backup/"
    echo ""
    echo "🛠️  Management Commands:"
    echo "   View logs: docker-compose logs -f [service]"
    echo "   Stop all: docker-compose down"
    echo "   Stop and remove: docker-compose down -v"
    echo "   Restart service: docker-compose restart [service]"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Access n8n at http://localhost:5678"
    echo "   2. Import workflows from ./workflows/ directory"
    echo "   3. Configure Gmail credentials in workflow"
    echo "   4. Test the stock trading workflow"
    echo ""
}

# Main execution
main() {
    echo "Starting Microsoft Stock Trading Platform..."
    
    check_docker
    check_docker_compose
    create_directories
    set_permissions
    check_environment
    pull_images
    start_services
    setup_ollama
    import_workflows
    health_check
    show_info
    
    print_success "Microsoft Stock Trading Platform is now running!"
    print_status "Press Ctrl+C to view logs, or run 'docker-compose logs -f' to monitor services"
    
    # Follow logs
    docker-compose -f $COMPOSE_FILE logs -f
}

# Handle interrupts
trap 'echo -e "\n� Shutting down..."; docker-compose -f $COMPOSE_FILE down; exit 0' INT TERM

# Run main function
main "$@"
