#!/bin/bash
# Health check script for production monitoring

set -e

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
WEB_URL="${WEB_URL:-http://localhost:80}"
TIMEOUT="${TIMEOUT:-10}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Status tracking
OVERALL_STATUS=0
CHECKS_PASSED=0
TOTAL_CHECKS=0

# Function to run a health check
run_check() {
    local name="$1"
    local command="$2"
    local description="$3"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking ${name}... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} - ${description}"
        OVERALL_STATUS=1
        return 1
    fi
}

echo "🔍 AgenTech Research Hub Health Check"
echo "======================================"

# API Health Checks
echo ""
echo "📡 API Health Checks:"
run_check "API Availability" "curl -f -s --max-time ${TIMEOUT} ${API_URL}/health" "API endpoint not responding"
run_check "API Root Endpoint" "curl -f -s --max-time ${TIMEOUT} ${API_URL}/" "Root endpoint not responding"
run_check "API Status" "curl -f -s --max-time ${TIMEOUT} ${API_URL}/status" "Status endpoint not responding"

# Web UI Health Checks
echo ""
echo "🌐 Web UI Health Checks:"
run_check "Web UI Availability" "curl -f -s --max-time ${TIMEOUT} ${WEB_URL}" "Web UI not responding"
run_check "Nginx Health" "curl -f -s --max-time ${TIMEOUT} ${WEB_URL}/nginx-health" "Nginx health endpoint not responding"

# Database Health Checks
echo ""
echo "🗄️ Database Health Checks:"
run_check "PostgreSQL Connection" "docker-compose exec -T postgres pg_isready -U agentech" "PostgreSQL not ready"
run_check "Database Tables" "docker-compose exec -T postgres psql -U agentech -d agentech_research_hub -c 'SELECT 1;'" "Database tables not accessible"

# Redis Health Checks
echo ""
echo "🔴 Redis Health Checks:"
run_check "Redis Connection" "docker-compose exec -T redis redis-cli ping" "Redis not responding"
run_check "Redis Memory" "docker-compose exec -T redis redis-cli info memory | grep used_memory_human" "Redis memory info not available"

# Container Health Checks
echo ""
echo "🐳 Container Health Checks:"
run_check "API Container" "docker-compose ps | grep agentech-research-hub | grep -q 'Up'" "API container not running"
run_check "Nginx Container" "docker-compose ps | grep agentech-nginx | grep -q 'Up'" "Nginx container not running"
run_check "PostgreSQL Container" "docker-compose ps | grep agentech-postgres | grep -q 'Up'" "PostgreSQL container not running"
run_check "Redis Container" "docker-compose ps | grep agentech-redis | grep -q 'Up'" "Redis container not running"

# Resource Health Checks
echo ""
echo "💾 Resource Health Checks:"
run_check "Disk Space" "[ $(df / | tail -1 | awk '{print $5}' | sed 's/%//') -lt 90 ]" "Disk usage above 90%"
run_check "Memory Usage" "[ $(free | grep Mem | awk '{printf \"%.0f\", $3/$2*100}') -lt 90 ]" "Memory usage above 90%"

# API Response Time Check
echo ""
echo "⚡ Performance Checks:"
response_time=$(curl -o /dev/null -s -w '%{time_total}' --max-time ${TIMEOUT} ${API_URL}/health 2>/dev/null || echo "0")
if (( $(echo "$response_time < 2.0" | bc -l) )); then
    echo -e "API Response Time... ${GREEN}✓ PASS${NC} (${response_time}s)"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    echo -e "API Response Time... ${RED}✗ FAIL${NC} - Response time too slow (${response_time}s)"
    OVERALL_STATUS=1
fi
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# Security Checks
echo ""
echo "🔒 Security Checks:"
run_check "Security Headers" "curl -I -s ${WEB_URL} | grep -q 'X-Frame-Options'" "Security headers not present"
run_check "SSL Redirect" "curl -I -s http://localhost | grep -q 'Location: https'" "SSL redirect not configured" || true

# Summary
echo ""
echo "======================================"
echo "📊 Health Check Summary:"
echo "   Checks Passed: ${CHECKS_PASSED}/${TOTAL_CHECKS}"

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "   Overall Status: ${GREEN}HEALTHY${NC} ✅"
    echo ""
    echo "🎉 All systems are operational!"
else
    echo -e "   Overall Status: ${RED}UNHEALTHY${NC} ❌"
    echo ""
    echo "⚠️  Some checks failed. Please review the output above."
fi

echo ""
echo "📈 System Information:"
echo "   Uptime: $(uptime -p 2>/dev/null || echo 'N/A')"
echo "   Load: $(uptime | awk -F'load average:' '{print $2}' 2>/dev/null || echo 'N/A')"
echo "   Timestamp: $(date)"

exit $OVERALL_STATUS
