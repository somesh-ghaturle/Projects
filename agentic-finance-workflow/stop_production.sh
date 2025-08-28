#!/bin/bash
# Stop production deployment

echo "🛑 Stopping Agentic Finance Workflow Production Deployment"

docker-compose -f docker-compose.production.yml down --remove-orphans

echo "✅ All services stopped"
