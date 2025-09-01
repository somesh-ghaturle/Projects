#!/bin/bash

# Advanced Multi-Agent Medical Assistant MCP Server - Production Deployment Script
# This script sets up and runs the complete medical assistant system with workflow orchestration

set -e

echo "🏥 Advanced Multi-Agent Medical Assistant MCP Server"
echo "=================================================="

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXECUTABLE="python3"
VENV_DIR="$PROJECT_ROOT/venv"
CONFIG_DIR="$PROJECT_ROOT/configs"
WORKFLOWS_DIR="$PROJECT_ROOT/workflows"
WEB_UI_DIR="$PROJECT_ROOT/web-ui"
LOGS_DIR="$PROJECT_ROOT/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available
check_python() {
    log_info "Checking Python installation..."
    if ! command -v $PYTHON_EXECUTABLE &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        exit 1
    fi

    PYTHON_VERSION=$($PYTHON_EXECUTABLE --version 2>&1 | awk '{print $2}')
    log_success "Python version: $PYTHON_VERSION"
}

# Create virtual environment
create_venv() {
    log_info "Creating virtual environment..."
    if [ ! -d "$VENV_DIR" ]; then
        $PYTHON_EXECUTABLE -m venv $VENV_DIR
        log_success "Virtual environment created at $VENV_DIR"
    else
        log_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    log_info "Activating virtual environment..."
    source $VENV_DIR/bin/activate
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
    log_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Dependencies installed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    mkdir -p $LOGS_DIR
    mkdir -p $CONFIG_DIR
    mkdir -p $WORKFLOWS_DIR
    mkdir -p $WEB_UI_DIR
    log_success "Directories created"
}

# Validate configuration files
validate_configs() {
    log_info "Validating configuration files..."

    # Check agent configuration
    if [ ! -f "$CONFIG_DIR/agents.yaml" ]; then
        log_error "Agent configuration file not found: $CONFIG_DIR/agents.yaml"
        exit 1
    fi

    # Check workflow files
    if [ ! -f "$WORKFLOWS_DIR/emergency_triage.yaml" ]; then
        log_warning "Emergency triage workflow not found: $WORKFLOWS_DIR/emergency_triage.yaml"
    fi

    if [ ! -f "$WORKFLOWS_DIR/routine_checkup.yaml" ]; then
        log_warning "Routine checkup workflow not found: $WORKFLOWS_DIR/routine_checkup.yaml"
    fi

    # Check web interface
    if [ ! -f "$WEB_UI_DIR/index.html" ]; then
        log_error "Web interface not found: $WEB_UI_DIR/index.html"
        exit 1
    fi

    log_success "Configuration validation completed"
}

# Health check function
health_check() {
    log_info "Performing health check..."

    # Check if port 8000 is available
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        log_warning "Port 8000 is already in use"
        return 1
    fi

    log_success "Health check passed"
    return 0
}

# Start the server
start_server() {
    log_info "Starting MCP Medical Assistant Server..."

    # Set environment variables
    export MCP_TRANSPORT="streamable-http"
    export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

    # Create log file
    LOG_FILE="$LOGS_DIR/server_$(date +%Y%m%d_%H%M%S).log"

    # Start server in background
    nohup python3 -m src.mcp_server.server > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!

    # Wait for server to start
    log_info "Waiting for server to start..."
    sleep 5

    # Check if server is running
    if kill -0 $SERVER_PID 2>/dev/null; then
        log_success "Server started successfully (PID: $SERVER_PID)"
        log_info "Server logs: $LOG_FILE"
        log_info "Web interface: http://localhost:8000"
        log_info "MCP endpoint: http://localhost:8000/mcp"

        # Save PID for later use
        echo $SERVER_PID > "$PROJECT_ROOT/server.pid"
    else
        log_error "Failed to start server"
        cat "$LOG_FILE"
        exit 1
    fi
}

# Stop the server
stop_server() {
    if [ -f "$PROJECT_ROOT/server.pid" ]; then
        SERVER_PID=$(cat "$PROJECT_ROOT/server.pid")
        if kill -0 $SERVER_PID 2>/dev/null; then
            log_info "Stopping server (PID: $SERVER_PID)..."
            kill $SERVER_PID
            sleep 2
            if kill -0 $SERVER_PID 2>/dev/null; then
                log_warning "Server didn't stop gracefully, force killing..."
                kill -9 $SERVER_PID
            fi
            log_success "Server stopped"
        else
            log_warning "Server process not found"
        fi
        rm -f "$PROJECT_ROOT/server.pid"
    else
        log_warning "Server PID file not found"
    fi
}

# Show status
show_status() {
    if [ -f "$PROJECT_ROOT/server.pid" ]; then
        SERVER_PID=$(cat "$PROJECT_ROOT/server.pid")
        if kill -0 $SERVER_PID 2>/dev/null; then
            log_success "Server is running (PID: $SERVER_PID)"
            log_info "Web interface: http://localhost:8000"
            log_info "Health check: curl http://localhost:8000/health"
        else
            log_warning "Server process not found, cleaning up..."
            rm -f "$PROJECT_ROOT/server.pid"
        fi
    else
        log_info "Server is not running"
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the medical assistant server"
    echo "  stop      - Stop the medical assistant server"
    echo "  restart   - Restart the medical assistant server"
    echo "  status    - Show server status"
    echo "  setup     - Initial setup (create venv, install dependencies)"
    echo "  logs      - Show recent server logs"
    echo "  health    - Perform health check"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 setup && $0 start"
    echo "  $0 logs"
}

# Main script logic
case "${1:-}" in
    "start")
        log_info "Starting Medical Assistant Server..."
        check_python
        create_directories
        validate_configs
        if health_check; then
            activate_venv
            start_server
        else
            log_error "Health check failed"
            exit 1
        fi
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        log_info "Restarting Medical Assistant Server..."
        stop_server
        sleep 2
        check_python
        create_directories
        validate_configs
        if health_check; then
            activate_venv
            start_server
        fi
        ;;
    "status")
        show_status
        ;;
    "setup")
        log_info "Setting up Medical Assistant environment..."
        check_python
        create_venv
        activate_venv
        install_dependencies
        create_directories
        log_success "Setup completed"
        ;;
    "logs")
        if [ -f "$PROJECT_ROOT/server.pid" ]; then
            LOG_FILE="$LOGS_DIR/server_$(date +%Y%m%d)*.log"
            if [ -f "$LOG_FILE" ]; then
                tail -f $LOG_FILE
            else
                log_warning "No log files found"
            fi
        else
            log_warning "Server is not running"
        fi
        ;;
    "health")
        if health_check; then
            log_success "System is healthy"
        else
            log_error "Health check failed"
        fi
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

echo ""
log_info "🏥 Advanced Multi-Agent Medical Assistant MCP Server"
log_info "=================================================="
log_info "Features:"
log_info "  • 4 Specialized AI Agents (Symptom Checker, Drug Info, Literature Search, Patient Interaction)"
log_info "  • Advanced Workflow Orchestration Engine"
log_info "  • Professional Web Interface with Analytics"
log_info "  • YAML-based Configuration Management"
log_info "  • Production-ready with Docker Support"
log_info "  • Real-time Health Monitoring"
echo ""
