#!/usr/bin/env python3
"""
Test script for AgenTech Research Hub API
"""

import requests
import json
import time
import sys


def test_api():
    """Test the running API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing AgenTech Research Hub API")
    print("=" * 40)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health check passed: {health_data['status']}")
            print(f"   📊 Uptime: {health_data['uptime']} seconds")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            root_data = response.json()
            print(f"   ✅ Root endpoint working: {root_data['name']} v{root_data['version']}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")
    
    # Test 3: Status endpoint
    print("\n3. Testing status endpoint...")
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            status_data = response.json()
            print(f"   ✅ Status endpoint working: {status_data['system']}")
            print(f"   🎯 Environment: {status_data['environment']}")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status endpoint error: {e}")
    
    # Test 4: Research endpoint (without API key)
    print("\n4. Testing research endpoint (no auth)...")
    try:
        research_data = {
            "query": "What is artificial intelligence?",
            "context": {}
        }
        response = requests.post(
            f"{base_url}/research", 
            json=research_data,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Research endpoint working")
            print(f"   📚 Query: {result['query']}")
            print(f"   📊 Sources found: {result['sources_found']}")
            print(f"   ⏱️ Execution time: {result['execution_time']}s")
        else:
            print(f"   ❌ Research endpoint failed: {response.status_code}")
            if response.content:
                print(f"   📝 Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Research endpoint error: {e}")
    
    # Test 5: API Documentation
    print("\n5. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("   ✅ API documentation accessible")
        else:
            print(f"   ❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API documentation error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 API Testing completed!")
    print(f"📍 Server running at: {base_url}")
    print(f"📖 Documentation: {base_url}/docs")
    print(f"❤️ Health Check: {base_url}/health")


if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    test_api()
