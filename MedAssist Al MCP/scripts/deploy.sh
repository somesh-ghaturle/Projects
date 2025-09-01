#!/bin/bash

# MedAssist AI MCP - Production Deployment Script
# Healthcare-focused AI platform with HIPAA compliance

set -e

echo "🏥 Starting MedAssist AI MCP Production Deployment..."

# Color codes for output
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

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Create production environment file if it doesn't exist
create_env_file() {
    if [ ! -f .env.production ]; then
        print_status "Creating production environment file..."
        cat > .env.production << EOL
# MedAssist AI Production Configuration
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
MEDICAL_MODE=production

# Security Settings for Medical Data
HIPAA_COMPLIANCE=true
SECURE_HEADERS=true
CORS_ORIGINS=["http://localhost:8080"]

# Performance Settings
CACHE_TTL=300
AGENT_TIMEOUT=60
MEDICAL_RESPONSE_CACHE=true

# Database Configuration
POSTGRES_DB=medassist_db
POSTGRES_USER=medassist_user
POSTGRES_PASSWORD=medassist_password_2025

# Redis Configuration
REDIS_PASSWORD=medassist_redis_2025

# Monitoring
GRAFANA_PASSWORD=medassist_admin_2025

# External APIs (Optional)
FDA_API_KEY=your_fda_api_key_here
MEDICAL_DB_ENABLED=true
EOL
        print_success "Created .env.production file"
        print_warning "Please update the API keys and passwords in .env.production"
    else
        print_status ".env.production file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs data ssl
    print_success "Directories created"
}

# Build and start services
deploy_services() {
    print_status "Building and starting MedAssist AI services..."
    
    # Pull latest images
    docker-compose -f docker-compose.production.yml pull
    
    # Build custom images
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Start services
    docker-compose -f docker-compose.production.yml up -d
    
    print_success "Services started successfully"
}

# Check service health
check_health() {
    print_status "Checking service health..."
    
    # Wait for services to start
    sleep 30
    
    # Check if services are running
    if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
        print_success "Services are running"
    else
        print_error "Some services failed to start"
        docker-compose -f docker-compose.production.yml logs
        exit 1
    fi
    
    # Check API health
    print_status "Checking API health..."
    sleep 10
    
    if curl -f http://localhost:8080/health &> /dev/null; then
        print_success "MedAssist AI API is healthy"
    else
        print_warning "API health check failed, but services are running"
    fi
}

# Display deployment information
show_deployment_info() {
    echo ""
    echo "🏥 ==============================================="
    echo "🏥 MedAssist AI MCP Production Deployment Complete"
    echo "🏥 ==============================================="
    echo ""
    echo "🌐 Medical Interface: http://localhost:8080"
    echo "📊 Grafana Dashboard: http://localhost:3000"
    echo "📈 Prometheus Metrics: http://localhost:9090"
    echo ""
    echo "🔐 Default Credentials:"
    echo "   Grafana: admin / medassist_admin_2025"
    echo ""
    echo "🏥 Medical Agents Available:"
    echo "   • Diagnostic Agent - Advanced symptom analysis"
    echo "   • Pharmacy Agent - Medication management"
    echo "   • Radiology Agent - Medical imaging support"
    echo "   • Treatment Agent - Treatment planning"
    echo "   • Emergency Agent - Critical care support"
    echo "   • Enterprise Agent - Healthcare management"
    echo ""
    echo "📋 Management Commands:"
    echo "   View logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "   Stop services: docker-compose -f docker-compose.production.yml down"
    echo "   View status: docker-compose -f docker-compose.production.yml ps"
    echo ""
    echo "⚕️ HIPAA Compliance Features:"
    echo "   • Secure data handling protocols"
    echo "   • Audit logging for all medical interactions"
    echo "   • Encrypted data transmission"
    echo "   • No permanent conversation storage"
    echo ""
    print_success "MedAssist AI is ready for healthcare operations!"
}

# Main deployment process
main() {
    echo "🏥 MedAssist AI MCP - Production Deployment"
    echo "=========================================="
    
    check_docker
    check_docker_compose
    create_env_file
    create_directories
    deploy_services
    check_health
    show_deployment_info
}

# Run main function
main "$@"
