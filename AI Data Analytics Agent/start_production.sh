#!/usr/bin/env bash
set -euo pipefail

echo "Building production image..."
docker-compose -f docker-compose.production.yml build --no-cache

echo "Starting production stack..."
docker-compose -f docker-compose.production.yml up -d

echo "Application should be available at http://localhost:8501"
