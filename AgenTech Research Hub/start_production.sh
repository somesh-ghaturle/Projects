#!/bin/bash
# Start AgenTech Research Hub in Production Mode

set -e

echo "🏭 Starting AgenTech Research Hub - Production Mode"
echo "=================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if environment file exists
if [ ! -f ".env" ]; then
    echo "⚠️ Creating default .env file..."
    cat > .env << 'EOF'
# AgenTech Research Hub Production Environment

# Application
APP_ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENABLE_API_KEY_AUTH=true

# Database (PostgreSQL)
POSTGRES_USER=agentech
POSTGRES_PASSWORD=secure_password_change_this
POSTGRES_DB=agentech_research_hub

# Redis
REDIS_PASSWORD=redis_password_change_this

# Security
SECRET_KEY=change_this_to_a_secure_random_key
API_KEY=your_production_api_key_here

# Features
ENABLE_WEB_SCRAPING=true
ENABLE_ACADEMIC_SEARCH=true
ENABLE_NEWS_SEARCH=true
EOF
    echo "📝 Created .env file. Please update the passwords and API keys!"
    echo "⚠️ Make sure to change the default passwords before running in production!"
fi

# Build and start production services
echo "📦 Building and starting production services..."
docker-compose -f docker-compose.production.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check database health
echo "🗄️ Checking database health..."
for i in {1..30}; do
    if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U agentech > /dev/null 2>&1; then
        echo "✅ Database is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Database failed to start properly"
        docker-compose -f docker-compose.production.yml logs postgres
        exit 1
    fi
    sleep 2
done

# Check API health
echo "❤️ Checking API health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ API failed to start properly"
        docker-compose -f docker-compose.production.yml logs agentech-api
        exit 1
    fi
    sleep 2
done

echo ""
echo "🎉 AgenTech Research Hub Production is now running!"
echo "🔧 API Server: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "❤️ Health Check: http://localhost:8000/health"
echo "🗄️ Database: localhost:5432"
echo "🚀 Redis: localhost:6379"
echo ""
echo "To stop the services, run: docker-compose -f docker-compose.production.yml down"
echo "To view logs, run: docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo "⚠️ Security Notes:"
echo "   - Change default passwords in .env file"
echo "   - Use proper SSL certificates in production"
echo "   - Set up proper firewall rules"
echo "   - Monitor logs regularly"
