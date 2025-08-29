#!/bin/bash

# Backup script for n8n Trading Workflow production data
# Creates backups of database, workflows, and configurations

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="n8n_backup_$TIMESTAMP"

echo "💾 Creating n8n Trading Workflow Backup"
echo "========================================"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup: $BACKUP_NAME"

# Create backup directory for this backup
mkdir -p "$BACKUP_DIR/$BACKUP_NAME"

# Backup PostgreSQL database
if docker-compose -f docker-compose.production.yml ps postgres >/dev/null 2>&1; then
    echo "🗄️  Backing up PostgreSQL database..."
    docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U n8n -d n8n > "$BACKUP_DIR/$BACKUP_NAME/database.sql"
    echo "✅ Database backup completed"
fi

# Backup n8n data volume
echo "📁 Backing up n8n data volume..."
docker run --rm -v n8n_data:/data -v "$(pwd)/$BACKUP_DIR/$BACKUP_NAME":/backup alpine tar czf /backup/n8n_data.tar.gz -C /data .
echo "✅ n8n data backup completed"

# Backup Redis data (if applicable)
if docker-compose -f docker-compose.production.yml ps redis >/dev/null 2>&1; then
    echo "🔄 Backing up Redis data..."
    docker run --rm -v redis_data:/data -v "$(pwd)/$BACKUP_DIR/$BACKUP_NAME":/backup alpine tar czf /backup/redis_data.tar.gz -C /data .
    echo "✅ Redis data backup completed"
fi

# Backup configuration files
echo "⚙️  Backing up configuration files..."
cp docker-compose.production.yml "$BACKUP_DIR/$BACKUP_NAME/"
cp trading-workflow.json "$BACKUP_DIR/$BACKUP_NAME/"
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/$BACKUP_NAME/"
fi
if [ -d "scripts" ]; then
    cp -r scripts "$BACKUP_DIR/$BACKUP_NAME/"
fi
echo "✅ Configuration backup completed"

# Create a restore script
cat > "$BACKUP_DIR/$BACKUP_NAME/restore.sh" << 'EOF'
#!/bin/bash
# Restore script for n8n Trading Workflow

set -e

echo "🔄 Restoring n8n Trading Workflow from backup"
echo "=============================================="

# Stop current containers
docker-compose -f docker-compose.production.yml down

# Restore database
if [ -f "database.sql" ]; then
    echo "🗄️  Restoring PostgreSQL database..."
    docker-compose -f docker-compose.production.yml up -d postgres
    sleep 10
    docker-compose -f docker-compose.production.yml exec -T postgres psql -U n8n -d n8n < database.sql
    echo "✅ Database restored"
fi

# Restore n8n data
if [ -f "n8n_data.tar.gz" ]; then
    echo "📁 Restoring n8n data..."
    docker volume rm n8n_data 2>/dev/null || true
    docker volume create n8n_data
    docker run --rm -v n8n_data:/data -v "$(pwd)":/backup alpine tar xzf /backup/n8n_data.tar.gz -C /data
    echo "✅ n8n data restored"
fi

# Restore Redis data
if [ -f "redis_data.tar.gz" ]; then
    echo "🔄 Restoring Redis data..."
    docker volume rm redis_data 2>/dev/null || true
    docker volume create redis_data
    docker run --rm -v redis_data:/data -v "$(pwd)":/backup alpine tar xzf /backup/redis_data.tar.gz -C /data
    echo "✅ Redis data restored"
fi

# Start all services
docker-compose -f docker-compose.production.yml up -d

echo "🎉 Restore completed!"
EOF

chmod +x "$BACKUP_DIR/$BACKUP_NAME/restore.sh"

# Create backup info file
cat > "$BACKUP_DIR/$BACKUP_NAME/backup_info.txt" << EOF
n8n Trading Workflow Backup
===========================

Backup Date: $(date)
Backup Name: $BACKUP_NAME
Docker Version: $(docker --version)
Docker Compose Version: $(docker-compose --version)

Contents:
- database.sql (PostgreSQL dump)
- n8n_data.tar.gz (n8n workflows and settings)
- redis_data.tar.gz (Redis cache data)
- Configuration files
- restore.sh (restoration script)

To restore this backup:
1. Copy this entire directory to your n8n installation
2. Run: ./restore.sh
EOF

# Create compressed archive
echo "🗜️  Creating compressed archive..."
cd "$BACKUP_DIR"
tar czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_NAME"
cd ..

echo ""
echo "✅ Backup completed successfully!"
echo "📁 Backup location: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "📊 Backup size: $(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)"
echo ""
echo "To restore this backup:"
echo "1. Extract: tar xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "2. Enter directory: cd $BACKUP_NAME"
echo "3. Run: ./restore.sh"
echo "========================================"
