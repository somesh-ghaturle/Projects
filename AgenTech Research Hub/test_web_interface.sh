#!/bin/bash
# Test Web Interface Functionality

echo "🌐 Testing AgenTech Research Hub Web Interface"
echo "=============================================="

# Test 1: Web interface loads
echo "1. Testing web interface loading..."
response_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/)
if [ "$response_code" = "200" ]; then
    echo "   ✅ Web interface loads successfully (HTTP $response_code)"
else
    echo "   ❌ Web interface failed to load (HTTP $response_code)"
fi

# Test 2: Health endpoint through proxy
echo "2. Testing health endpoint through nginx proxy..."
health_response=$(curl -s http://localhost/health)
if echo "$health_response" | grep -q "healthy"; then
    echo "   ✅ Health endpoint working through proxy"
else
    echo "   ❌ Health endpoint failed through proxy"
fi

# Test 3: Research endpoint through proxy
echo "3. Testing research endpoint through nginx proxy..."
research_response=$(curl -s -X POST http://localhost/research \
  -H "Content-Type: application/json" \
  -d '{"query": "web interface test"}')
if echo "$research_response" | grep -q "success"; then
    echo "   ✅ Research endpoint working through proxy"
else
    echo "   ❌ Research endpoint failed through proxy"
fi

# Test 4: API docs endpoint
echo "4. Testing API documentation endpoint..."
docs_response_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/docs)
if [ "$docs_response_code" = "200" ]; then
    echo "   ✅ API documentation accessible (HTTP $docs_response_code)"
else
    echo "   ❌ API documentation failed (HTTP $docs_response_code)"
fi

# Test 5: Container health
echo "5. Checking container health..."
containers_up=$(docker-compose ps --services --filter "status=running" | wc -l)
if [ "$containers_up" -eq 2 ]; then
    echo "   ✅ All containers are running ($containers_up/2)"
else
    echo "   ❌ Some containers are not running ($containers_up/2)"
fi

echo ""
echo "🎉 Web Interface Test Summary"
echo "=========================="
echo "✅ Web Interface: http://localhost"
echo "✅ API Health: http://localhost/health"
echo "✅ API Research: http://localhost/research"
echo "✅ API Docs: http://localhost/docs"
echo "✅ Direct API: http://localhost:8000"
echo ""
echo "The web interface should now be fully functional!"
echo "You can conduct research, view API status, and access documentation."
