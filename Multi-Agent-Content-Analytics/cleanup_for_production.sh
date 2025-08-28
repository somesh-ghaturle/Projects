#!/bin/bash

echo "🧹 Cleaning up unnecessary files for production..."

# Create backup directory if it doesn't exist
if [ ! -d "./production_cleanup_backup" ]; then
  mkdir -p ./production_cleanup_backup
fi

# Timestamp for the backup
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Move frontend directory to backup (keeping only web_interface.html)
if [ -d "./frontend" ]; then
  echo "📦 Backing up frontend directory..."
  cp -r ./frontend ./production_cleanup_backup/frontend_$TIMESTAMP
  rm -rf ./frontend
fi

# Make sure content_analytics_ui.html is properly set up
if [ -f "./content_analytics_ui.html" ] && [ ! -f "./web_interface.html" ]; then
  echo "🔄 Renaming content_analytics_ui.html to web_interface.html..."
  cp ./content_analytics_ui.html ./web_interface.html
fi

# Remove any development-specific files
echo "🗑️ Removing development-specific files..."
rm -f ./docker-compose.yml
cp ./docker-compose.production.yml ./docker-compose.yml

# Ensure executable permissions for scripts
echo "🔒 Setting executable permissions for scripts..."
chmod +x ./start_production.sh
chmod +x ./stop_production.sh

echo "✅ Cleanup complete! Ready for production deployment."
