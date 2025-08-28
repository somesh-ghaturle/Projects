#!/bin/bash

# Production-Only Cleanup Script
# This script will remove all files and directories not needed for production

echo "🔄 Starting thorough production-only cleanup..."

# Create production backup directory if it doesn't exist
BACKUP_DIR="production_cleanup_backup"
mkdir -p "$BACKUP_DIR"

# Define essential production files and directories
ESSENTIAL_FILES=(
  # Core application files
  ".env"
  "Dockerfile.production"
  "docker-compose.production.yml"
  "multi_agent_content_api.py" 
  "content_analytics_ui.html"
  "web_interface.html"
  "requirements.txt"
  "PRODUCTION_OPTIMIZATION.md"
  "README.md"
  # Production scripts
  "start_production.sh"
  "stop_production.sh"
  "cleanup_for_production.sh"
)

ESSENTIAL_DIRS=(
  "app"
  "frontend"
  "logs"
  "cache"
  "$BACKUP_DIR"
)

# Function to backup and remove a file
backup_and_remove_file() {
  local file="$1"
  if [ -f "$file" ]; then
    echo "📦 Backing up and removing: $file"
    # Create directory structure in backup folder
    mkdir -p "$BACKUP_DIR/$(dirname "$file")"
    # Copy file to backup
    cp "$file" "$BACKUP_DIR/$file"
    # Remove original file
    rm "$file"
  fi
}

# Identify and remove non-essential files
echo "🔍 Identifying non-essential files..."
find . -type f -not -path "./$BACKUP_DIR/*" | while read -r file; do
  # Remove leading ./
  file="${file#./}"
  
  # Skip essential files
  is_essential=false
  for essential in "${ESSENTIAL_FILES[@]}"; do
    if [ "$file" == "$essential" ]; then
      is_essential=true
      break
    fi
  done
  
  # Skip files in essential directories
  for dir in "${ESSENTIAL_DIRS[@]}"; do
    if [[ "$file" == "$dir"/* ]]; then
      is_essential=true
      break
    fi
  done
  
  # Backup and remove non-essential files
  if [ "$is_essential" = false ]; then
    backup_and_remove_file "$file"
  fi
done

# Clean up any __pycache__ directories
echo "🧹 Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} +

# Empty log and cache directories but keep the folders
echo "🧹 Cleaning log directory..."
rm -f logs/*
echo "🧹 Cleaning cache directory..."
rm -f cache/*

# Create placeholder files to keep directories in git
touch logs/.keep
touch cache/.keep

# Rename production files to standard names
echo "🔄 Renaming production files to standard names..."

# Backup the original files first
if [ -f "Dockerfile" ]; then
  cp "Dockerfile" "$BACKUP_DIR/Dockerfile.original"
fi
if [ -f "docker-compose.yml" ]; then
  cp "docker-compose.yml" "$BACKUP_DIR/docker-compose.yml.original"
fi
if [ -f "start.sh" ]; then
  cp "start.sh" "$BACKUP_DIR/start.sh.original"
fi
if [ -f "stop.sh" ]; then
  cp "stop.sh" "$BACKUP_DIR/stop.sh.original"
fi

# Now replace them with production versions
cp "Dockerfile.production" "Dockerfile"
cp "docker-compose.production.yml" "docker-compose.yml"
cp "start_production.sh" "start.sh"
cp "stop_production.sh" "stop.sh"

# Remove the duplicates
rm -f "Dockerfile.production"
rm -f "docker-compose.production.yml"
rm -f "start_production.sh"
rm -f "stop_production.sh"

# List what's left
echo "✅ Production-only cleanup complete!"
echo "📊 Final directory structure:"
find . -type f -not -path "./$BACKUP_DIR/*" | sort

echo "🗄️ Backup of removed files stored in: $BACKUP_DIR/"
echo "🚀 Your project is now ready for production use!"
