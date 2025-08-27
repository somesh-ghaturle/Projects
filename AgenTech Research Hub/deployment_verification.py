#!/usr/bin/env python3
"""
AgenTech Research Hub - Deployment Verification Script
=====================================================

This script verifies that the AgenTech Research Hub is properly deployed and functioning.
"""

import requests
import json
import time
import sys

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check: PASSED")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            return True
        else:
            print(f"❌ Health Check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: FAILED ({str(e)})")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root Endpoint: PASSED")
            print(f"   Name: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print(f"❌ Root Endpoint: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Root Endpoint: FAILED ({str(e)})")
        return False

def test_research_endpoint():
    """Test the research endpoint"""
    try:
        payload = {
            "query": "What are the latest developments in quantum computing?",
            "max_sources": 3
        }
        response = requests.post(
            "http://localhost:8000/research", 
            json=payload, 
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Research Endpoint: PASSED")
            print(f"   Query: {data.get('query')}")
            print(f"   Sources Found: {data.get('sources_found')}")
            print(f"   Quality Score: {data.get('quality_score')}")
            return True
        else:
            print(f"❌ Research Endpoint: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Research Endpoint: FAILED ({str(e)})")
        return False

def main():
    """Main verification function"""
    print("🚀 AgenTech Research Hub - Deployment Verification")
    print("=" * 55)
    print()
    
    tests = [
        test_health_endpoint,
        test_root_endpoint,
        test_research_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 55)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 DEPLOYMENT SUCCESSFUL! All systems operational.")
        print()
        print("🌐 Available Endpoints:")
        print("   • Health Check: http://localhost:8000/health")
        print("   • API Root: http://localhost:8000/")
        print("   • Research API: http://localhost:8000/research")
        print("   • Interactive Docs: http://localhost:8000/docs")
        print()
        print("🤖 Your AgenTech Research Hub is ready to process research queries!")
        sys.exit(0)
    else:
        print("❌ DEPLOYMENT ISSUES DETECTED")
        print("Please check the server logs and ensure the API server is running.")
        sys.exit(1)

if __name__ == "__main__":
    main()
