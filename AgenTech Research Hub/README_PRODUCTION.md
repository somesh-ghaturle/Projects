# AgenTech Research Hub - Production Deployment Guide 🚀

> **Enterprise-Grade AI Research Platform with Production-Ready Architecture**

[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](https://github.com/yourusername/agentech-research-hub)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![Security](https://img.shields.io/badge/Security-Hardened-red.svg)](https://owasp.org/)
[![Monitoring](https://img.shields.io/badge/Monitoring-Enabled-orange.svg)](https://prometheus.io/)

## 🏗️ Production Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │     Nginx        │    │   Web UI        │
│   (Nginx)       │────│   (Reverse       │────│   (Static)      │
│                 │    │    Proxy)        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │
         │              ┌─────────────────┐
         │              │   FastAPI       │
         └──────────────│   Application   │
                        │   (Multi-worker)│
                        └─────────────────┘
                                 │
                    ┌─────────────────────────────┐
                    │                             │
         ┌─────────────────┐           ┌─────────────────┐
         │   PostgreSQL    │           │     Redis       │
         │   (Database)    │           │   (Cache/Queue) │
         └─────────────────┘           └─────────────────┘
                    │                             │
         ┌─────────────────┐           ┌─────────────────┐
         │   Celery        │           │   Monitoring    │
         │   Workers       │           │ (Prometheus/    │
         └─────────────────┘           │  Grafana)       │
                                       └─────────────────┘
```

## 🚀 Quick Production Deployment

### Prerequisites

- **Docker Engine** 20.10+ and **Docker Compose** 2.0+
- **4GB RAM** minimum (8GB recommended)
- **20GB disk space** minimum
- **Linux/macOS** (Windows with WSL2)

### 1-Command Deployment

```bash
# Clone and deploy
git clone <your-repo-url>
cd "AgenTech Research Hub"
chmod +x scripts/deploy.sh
./scripts/deploy.sh production
```

### Manual Deployment Steps

```bash
# 1. Environment Setup
cp .env.production .env
# Edit .env with your production values

# 2. Build and Deploy
docker-compose -f docker-compose.production.yml up -d

# 3. Verify Deployment
./scripts/health_check.sh
```

## 🔧 Configuration

### Environment Variables

Create `.env.production` with your production settings:

```bash
# Application
APP_ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your_super_secure_secret_key

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:password@postgres:5432/agentech_research_hub

# API Keys (Required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# Security
CORS_ALLOWED_ORIGINS=["https://yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com", "api.yourdomain.com"]

# Performance
MAX_CONCURRENT_AGENTS=10
RATE_LIMIT_PER_MINUTE=100
RESEARCH_TIMEOUT_SECONDS=180
```

### SSL/TLS Configuration

For production HTTPS:

```bash
# 1. Obtain SSL certificates (Let's Encrypt recommended)
certbot certonly --standalone -d yourdomain.com

# 2. Copy certificates to nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem

# 3. Enable HTTPS in nginx/nginx.conf
# Uncomment the HTTPS server block
```

## 🔒 Security Features

### Built-in Security

- **Rate Limiting**: API and web requests
- **API Key Authentication**: Secure endpoint access
- **CORS Protection**: Configurable origins
- **Security Headers**: OWASP recommended headers
- **Input Validation**: Pydantic schema validation
- **SQL Injection Prevention**: SQLAlchemy ORM
- **XSS Protection**: Content Security Policy

### Security Hardening

```bash
# 1. Enable API key authentication
echo "ENABLE_API_KEY_AUTH=True" >> .env.production

# 2. Configure firewall (example for UFW)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 3. Set up fail2ban (optional)
sudo apt-get install fail2ban
```

## 📊 Monitoring & Observability

### Built-in Monitoring Stack

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Health Checks**: Automated system monitoring
- **Structured Logging**: JSON formatted logs
- **Error Tracking**: Sentry integration (optional)

### Access Monitoring

```bash
# Grafana Dashboard
http://localhost:3001
# Default: admin/admin123

# Prometheus Metrics
http://localhost:9090

# Application Metrics
http://localhost:8000/metrics
```

### Health Monitoring

```bash
# Automated health checks
./scripts/health_check.sh

# Manual endpoint checks
curl http://localhost:8000/health
curl http://localhost:80/nginx-health
```

## 🚀 Performance Optimization

### Production Scaling

#### Horizontal Scaling

```yaml
# docker-compose.production.yml
services:
  agentech-api:
    deploy:
      replicas: 3  # Scale API servers
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
```

#### Database Optimization

```sql
-- PostgreSQL tuning
-- Add to postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

#### Caching Strategy

```python
# Redis caching configuration
REDIS_CACHE_TTL = 3600  # 1 hour
ENABLE_QUERY_CACHING = True
CACHE_RESEARCH_RESULTS = True
```

### Performance Monitoring

```bash
# Resource monitoring
docker stats

# Application performance
curl http://localhost:8000/metrics-summary
```

## 🔄 Backup & Recovery

### Automated Backups

```bash
# Database backup script
#!/bin/bash
docker-compose exec postgres pg_dump -U agentech agentech_research_hub > backup_$(date +%Y%m%d).sql

# Schedule with cron
0 2 * * * /path/to/backup_script.sh
```

### Data Recovery

```bash
# Restore from backup
docker-compose exec -T postgres psql -U agentech agentech_research_hub < backup_20241201.sql
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Not Starting

```bash
# Check logs
docker-compose logs agentech-api

# Common fixes
docker-compose down
docker system prune -f
docker-compose up -d
```

#### 2. Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready -U agentech

# Reset database
docker-compose down -v
docker-compose up -d
```

#### 3. High Memory Usage

```bash
# Monitor memory
docker stats

# Restart services
docker-compose restart agentech-api
```

### Debug Mode

```bash
# Enable debug logging
echo "LOG_LEVEL=DEBUG" >> .env.production
docker-compose restart agentech-api
```

## 📈 Deployment Environments

### Staging Environment

```bash
# Deploy to staging
./scripts/deploy.sh staging

# Staging-specific configuration
cp .env.staging .env
```

### Production Environment

```bash
# Deploy to production
./scripts/deploy.sh production

# Production-specific configuration
cp .env.production .env
```

## 🔧 Maintenance

### Regular Maintenance Tasks

```bash
# 1. Update dependencies
docker-compose pull
docker-compose up -d

# 2. Clean up unused resources
docker system prune -f

# 3. Monitor disk space
df -h

# 4. Check logs
docker-compose logs --tail=100 agentech-api
```

### Updates and Upgrades

```bash
# 1. Backup data
./scripts/backup.sh

# 2. Pull latest code
git pull origin main

# 3. Rebuild and deploy
docker-compose build --no-cache
docker-compose up -d

# 4. Verify deployment
./scripts/health_check.sh
```

## 📊 API Documentation

### Production Endpoints

- **Web UI**: `https://yourdomain.com`
- **API Base**: `https://api.yourdomain.com`
- **Health Check**: `https://api.yourdomain.com/health`
- **API Docs**: `https://api.yourdomain.com/docs` (if enabled)

### API Authentication

```bash
# Using API key
curl -H "X-API-Key: your-api-key" https://api.yourdomain.com/research
```

## 🎯 Best Practices

### Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups scheduled
- [ ] Monitoring alerts configured
- [ ] Log rotation enabled
- [ ] Security headers verified
- [ ] Rate limiting tested
- [ ] Load testing completed
- [ ] Disaster recovery plan documented

### Monitoring Checklist

- [ ] Uptime monitoring active
- [ ] Error rate alerts configured
- [ ] Performance metrics tracked
- [ ] Log aggregation setup
- [ ] Security monitoring enabled

## 🆘 Support

### Production Support

- **Documentation**: Check this README and inline documentation
- **Logs**: `docker-compose logs -f agentech-api`
- **Health Check**: `./scripts/health_check.sh`
- **Monitoring**: Grafana dashboard at http://localhost:3001

### Emergency Procedures

```bash
# Quick restart
docker-compose restart agentech-api

# Full system restart
docker-compose down && docker-compose up -d

# Emergency stop
docker-compose down
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

**🚀 Ready for Production!** This configuration provides enterprise-grade reliability, security, and scalability for your AgenTech Research Hub deployment.
