#!/bin/bash

echo "🛑 Stopping Multi-Agent Content Analytics..."

# Stop and remove containers
docker-compose down

echo "✅ All containers stopped and removed."

# Optional: Remove images (uncomment if you want to clean everything)
# echo "🗑️  Removing Docker images..."
# docker-compose down --rmi all

echo "📊 Remaining containers:"
docker ps -a --filter "name=multi-agent"
