#!/bin/bash

echo "🛑 Stopping Multi-Agent Content Analytics PRODUCTION environment..."

# Stop and remove containers
docker-compose -f docker-compose.production.yml down

echo "✅ All production containers stopped and removed."

# List any remaining containers
echo "📊 Remaining containers:"
docker ps -a --filter "name=multi-agent"
