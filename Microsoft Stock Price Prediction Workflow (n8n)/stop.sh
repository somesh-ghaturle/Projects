#!/bin/bash

# Stop n8n Trading Workflow
# This script stops all running containers

set -e

echo "🛑 Stopping n8n Trading Workflow"
echo "================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running."
    exit 1
fi

# Determine which compose file to use
if [ "$1" = "production" ] || [ "$1" = "prod" ]; then
    COMPOSE_FILE="docker-compose.production.yml"
    echo "🔧 Stopping production environment..."
else
    COMPOSE_FILE="docker-compose.yml"
    echo "🔧 Stopping development environment..."
fi

# Stop containers
if [ -f "$COMPOSE_FILE" ]; then
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    echo "✅ Containers stopped successfully"
else
    echo "❌ Error: $COMPOSE_FILE not found"
    exit 1
fi

# Optional: Remove volumes (uncomment if you want to reset data)
# echo "🗑️  Removing data volumes..."
# docker volume rm n8n_data postgres_data redis_data 2>/dev/null || true

echo "🎉 n8n Trading Workflow stopped!"
echo "================================="
