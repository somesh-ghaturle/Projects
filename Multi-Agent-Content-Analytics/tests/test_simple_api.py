"""
Tests for the simple FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Import the simple app
from simple_app import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Multi-Agent Content Analytics API" in data["message"]
    assert data["status"] == "running"

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "API is running successfully" in data["message"]
    assert data["version"] == "1.0.0"

def test_analyze_content():
    """Test the content analysis endpoint"""
    test_content = "This is a sample movie script content for testing the analysis functionality."
    
    response = client.post("/analyze", json={
        "content": test_content,
        "analysis_type": "script"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["content"] == test_content
    assert data["analysis_type"] == "script"
    assert "results" in data
    assert "word_count" in data["results"]
    assert "sentiment" in data["results"]
    assert data["results"]["word_count"] == len(test_content.split())

def test_analyze_content_default_type():
    """Test content analysis with default analysis type"""
    test_content = "Short test content."
    
    response = client.post("/analyze", json={
        "content": test_content
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["analysis_type"] == "basic"

def test_list_agents():
    """Test listing available agents"""
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    
    assert "agents" in data
    assert len(data["agents"]) == 3
    
    agent_names = [agent["name"] for agent in data["agents"]]
    assert "script_summarizer" in agent_names
    assert "genre_classifier" in agent_names
    assert "marketing_agent" in agent_names

def test_get_specific_agent():
    """Test getting information about a specific agent"""
    response = client.get("/agents/script_summarizer")
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "Script Summarizer Agent"
    assert "capabilities" in data
    assert "models" in data
    assert data["status"] == "ready"

def test_get_nonexistent_agent():
    """Test getting information about a non-existent agent"""
    response = client.get("/agents/nonexistent_agent")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert "not found" in data["error"]

def test_content_analysis_long_content():
    """Test content analysis with long content (should be truncated in response)"""
    long_content = "This is a very long content. " * 20  # Make it long
    
    response = client.post("/analyze", json={
        "content": long_content,
        "analysis_type": "detailed"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Content should be truncated to 100 chars + "..."
    assert len(data["content"]) <= 103  # 100 + "..."
    assert data["content"].endswith("...")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
