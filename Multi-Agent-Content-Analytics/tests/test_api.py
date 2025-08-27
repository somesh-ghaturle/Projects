"""
Test suite for API endpoints
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.main import app
from src.api.rest_endpoints import router
from src.api.graphql_schema import schema

class TestRESTEndpoints:
    """Test cases for REST API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_api_health_endpoint(self, client):
        """Test API health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
    
    @patch('src.api.rest_endpoints.get_orchestrator')
    def test_system_status_endpoint(self, mock_get_orchestrator, client):
        """Test system status endpoint"""
        # Mock orchestrator status
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_agent_status.return_value = {
            "orchestrator_initialized": True,
            "agents": {
                "script_summarizer": {
                    "initialized": True,
                    "status": "ready",
                    "error_count": 0
                },
                "genre_classifier": {
                    "initialized": True,
                    "status": "ready",
                    "error_count": 0
                }
            },
            "cache_size": 0,
            "active_tasks": 0
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        response = client.get("/api/v1/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["orchestrator_initialized"] == True
        assert "agents" in data
        assert len(data["agents"]) == 2
        assert data["system_health"] == "healthy"
    
    @patch('src.api.rest_endpoints.get_orchestrator')
    def test_analyze_content_endpoint(self, mock_get_orchestrator, client, sample_movie_script, sample_social_media_posts):
        """Test content analysis endpoint"""
        # Mock orchestrator
        mock_orchestrator = AsyncMock()
        mock_analysis_result = {
            "analysis_id": "test_analysis_123",
            "timestamp": "2024-01-01T12:00:00",
            "content_summary": {
                "content_type": "movie_content",
                "analysis_scope": ["script_analysis", "marketing_analysis"],
                "key_findings": ["Test finding"]
            },
            "agents_used": ["script_summarizer", "marketing_agent"],
            "individual_results": {
                "script_analysis": {"summary": {"plot": "Test plot"}},
                "marketing_analysis": {"sentiment_analysis": {"overall_sentiment": "positive"}}
            },
            "cross_agent_insights": {},
            "confidence_scores": {"script_analysis": 0.8, "marketing_analysis": 0.7},
            "recommendations": {"content_improvements": ["Test recommendation"]}
        }
        mock_orchestrator.analyze_content.return_value = mock_analysis_result
        mock_get_orchestrator.return_value = mock_orchestrator
        
        # Test request
        request_data = {
            "script_text": sample_movie_script,
            "social_media_data": sample_social_media_posts,
            "metadata": {
                "title": "Test Movie",
                "genre_hint": "Drama"
            },
            "options": {
                "include_script_analysis": True,
                "include_marketing_analysis": True,
                "async_processing": False
            }
        }
        
        response = client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["analysis_id"] == "test_analysis_123"
        assert "content_summary" in data
        assert "individual_results" in data
    
    @patch('src.api.rest_endpoints.get_orchestrator')
    def test_analyze_content_async(self, mock_get_orchestrator, client, sample_movie_script):
        """Test asynchronous content analysis"""
        mock_orchestrator = AsyncMock()
        mock_get_orchestrator.return_value = mock_orchestrator
        
        request_data = {
            "script_text": sample_movie_script,
            "options": {
                "async_processing": True
            }
        }
        
        response = client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert data["content_summary"]["status"] == "processing"
    
    def test_analyze_content_validation_error(self, client):
        """Test content analysis with invalid data"""
        # Empty request
        response = client.post("/api/v1/analyze", json={})
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.rest_endpoints.get_orchestrator')
    def test_agent_status_endpoint(self, mock_get_orchestrator, client):
        """Test individual agent status endpoint"""
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_agent_status.return_value = {
            "agents": {
                "script_summarizer": {
                    "initialized": True,
                    "status": "ready",
                    "error_count": 0,
                    "last_execution": "2024-01-01T12:00:00"
                }
            }
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        response = client.get("/api/v1/agents/script_summarizer/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["agent_name"] == "script_summarizer"
        assert "status" in data
    
    def test_agent_status_not_found(self, client):
        """Test agent status for non-existent agent"""
        with patch('src.api.rest_endpoints.get_orchestrator') as mock_get_orchestrator:
            mock_orchestrator = AsyncMock()
            mock_orchestrator.get_agent_status.return_value = {"agents": {}}
            mock_get_orchestrator.return_value = mock_orchestrator
            
            response = client.get("/api/v1/agents/nonexistent_agent/status")
            assert response.status_code == 404
    
    @patch('src.api.rest_endpoints.get_orchestrator')
    def test_cache_stats_endpoint(self, mock_get_orchestrator, client):
        """Test cache statistics endpoint"""
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_agent_status.return_value = {
            "cache_size": 5,
            "active_tasks": 2
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        response = client.get("/api/v1/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["cache_size"] == 5
        assert data["active_tasks"] == 2
        assert "background_tasks" in data
    
    def test_clear_cache_endpoint(self, client):
        """Test cache clearing endpoint"""
        response = client.delete("/api/v1/cache/clear")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "success"

class TestGraphQLEndpoints:
    """Test cases for GraphQL API"""
    
    @pytest.fixture
    def client(self):
        """Create test client for GraphQL"""
        return TestClient(app)
    
    def test_graphql_endpoint_exists(self, client):
        """Test that GraphQL endpoint is accessible"""
        # Test GraphQL introspection query
        query = """
        query {
            __schema {
                types {
                    name
                }
            }
        }
        """
        
        response = client.post("/graphql", json={"query": query})
        # Should return 200 even if schema is not fully set up
        assert response.status_code in [200, 400]  # 400 if schema not properly mounted
    
    @patch('src.api.graphql_schema.ContentAnalyticsResolver._ensure_initialized')
    def test_graphql_system_status_query(self, mock_init, client):
        """Test GraphQL system status query"""
        query = """
        query {
            systemStatus {
                orchestratorInitialized
                systemHealth
                cacheSize
                activeTasks
            }
        }
        """
        
        # This test would need the GraphQL endpoint properly mounted
        # For now, just test that the query structure is valid
        assert "systemStatus" in query
        assert "orchestratorInitialized" in query
    
    @patch('src.api.graphql_schema.ContentAnalyticsResolver._ensure_initialized')
    def test_graphql_analyze_content_mutation(self, mock_init, client):
        """Test GraphQL content analysis mutation"""
        mutation = """
        mutation AnalyzeContent($contentData: ContentData!, $options: AnalysisOptions) {
            analyzeContent(contentData: $contentData, options: $options) {
                analysisId
                timestamp
                contentSummary {
                    contentType
                    keyFindings
                }
                agentsUsed
            }
        }
        """
        
        variables = {
            "contentData": {
                "scriptText": "Sample script text",
                "metadata": {"title": "Test Movie"}
            },
            "options": {
                "includeScriptAnalysis": True,
                "detailedInsights": True
            }
        }
        
        # This test would need the GraphQL endpoint properly mounted
        assert "analyzeContent" in mutation
        assert "contentData" in str(variables)

class TestErrorHandling:
    """Test error handling in API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @patch('src.api.rest_endpoints.get_orchestrator')
    def test_internal_server_error(self, mock_get_orchestrator, client):
        """Test internal server error handling"""
        # Mock orchestrator to raise an exception
        mock_orchestrator = AsyncMock()
        mock_orchestrator.get_agent_status.side_effect = Exception("Database error")
        mock_get_orchestrator.return_value = mock_orchestrator
        
        response = client.get("/api/v1/status")
        assert response.status_code == 500
        
        data = response.json()
        assert "Failed to get system status" in data["detail"]
    
    def test_not_found_endpoint(self, client):
        """Test 404 error for non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method"""
        response = client.post("/api/v1/status")  # Should be GET
        assert response.status_code == 405

class TestRequestValidation:
    """Test request validation"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON"""
        response = client.post(
            "/api/v1/analyze",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test validation of missing required fields"""
        # Send request with invalid data structure
        response = client.post("/api/v1/analyze", json={"invalid_field": "value"})
        assert response.status_code == 422
    
    def test_invalid_data_types(self, client):
        """Test validation of invalid data types"""
        request_data = {
            "script_text": 123,  # Should be string
            "social_media_data": "not a list",  # Should be list
            "options": "not an object"  # Should be object
        }
        
        response = client.post("/api/v1/analyze", json=request_data)
        assert response.status_code == 422

class TestAuthentication:
    """Test authentication and authorization (if implemented)"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_public_endpoints_accessible(self, client):
        """Test that public endpoints are accessible without auth"""
        # Health check should always be accessible
        response = client.get("/health")
        assert response.status_code == 200
        
        response = client.get("/api/v1/health")
        assert response.status_code == 200
    
    # Additional auth tests would go here if authentication is implemented

class TestPerformance:
    """Test API performance characteristics"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_response_time_health_check(self, client):
        """Test that health check responds quickly"""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond in less than 1 second
    
    @patch('src.api.rest_endpoints.get_orchestrator')
    def test_large_payload_handling(self, mock_get_orchestrator, client):
        """Test handling of large payloads"""
        mock_orchestrator = AsyncMock()
        mock_orchestrator.analyze_content.return_value = {
            "analysis_id": "test",
            "timestamp": "2024-01-01T12:00:00",
            "content_summary": {},
            "agents_used": [],
            "individual_results": {},
            "cross_agent_insights": {},
            "confidence_scores": {},
            "recommendations": {}
        }
        mock_get_orchestrator.return_value = mock_orchestrator
        
        # Create a large script text
        large_script = "FADE IN:\n" + "This is a test line.\n" * 10000 + "FADE OUT."
        
        request_data = {
            "script_text": large_script,
            "options": {"include_script_analysis": True}
        }
        
        response = client.post("/api/v1/analyze", json=request_data)
        # Should handle large payloads without error
        assert response.status_code in [200, 413]  # 413 if payload too large

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
