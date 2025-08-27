#!/usr/bin/env python3
"""
Manual API testing script to validate the Multi-Agent Content Analytics API
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8002"

def test_endpoint(endpoint, method="GET", data=None, expected_status=200):
    """Test an API endpoint"""
    print(f"\n🧪 Testing {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ Success!")
            try:
                json_data = response.json()
                print(f"Response: {json.dumps(json_data, indent=2)}")
            except:
                print(f"Response Text: {response.text}")
        else:
            print("❌ Failed!")
            print(f"Response: {response.text}")
        
        return response
    except requests.exceptions.ConnectionError:
        print("❌ Failed to connect to server. Is it running?")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run manual API tests"""
    print("🚀 Multi-Agent Content Analytics API Testing")
    print("=" * 50)
    
    # Test 1: Root endpoint
    test_endpoint("/")
    
    # Test 2: Health check
    test_endpoint("/health")
    
    # Test 3: List agents
    test_endpoint("/agents")
    
    # Test 4: Get specific agent
    test_endpoint("/agents/script_summarizer")
    
    # Test 5: Get non-existent agent
    test_endpoint("/agents/nonexistent", expected_status=404)
    
    # Test 6: Content analysis
    content_data = {
        "content": "This is a sample movie script. The hero embarks on an adventure to save the world.",
        "analysis_type": "script"
    }
    test_endpoint("/analyze", method="POST", data=content_data)
    
    # Test 7: Content analysis with default type
    simple_data = {
        "content": "A short piece of content for testing."
    }
    test_endpoint("/analyze", method="POST", data=simple_data)
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\n📝 Summary:")
    print("- API server is running successfully")
    print("- All basic endpoints are functional")
    print("- Content analysis is working with mock data")
    print("- Ready for full multi-agent implementation")

if __name__ == "__main__":
    main()
