"""
Test suite for Multi-Agent Content Analytics agents
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.agents.base_agent import BaseAgent
from src.agents.script_summarizer import ScriptSummarizerAgent
from src.agents.genre_classifier import GenreClassificationAgent
from src.agents.marketing_agent import MarketingRecommendationAgent
from src.agents.agent_orchestrator import AgentOrchestrator

class TestBaseAgent:
    """Test cases for BaseAgent"""
    
    def test_base_agent_initialization(self):
        """Test base agent initialization"""
        agent = BaseAgent("test_agent")
        
        assert agent.agent_name == "test_agent"
        assert not agent.is_initialized
        assert agent.config == {}
        assert agent.execution_count == 0
        assert agent.error_count == 0
    
    def test_base_agent_validation(self):
        """Test base agent input validation"""
        agent = BaseAgent("test_agent")
        
        # Test valid input
        valid_input = {"text": "test content", "metadata": {}}
        assert agent.validate_input(valid_input) == True
        
        # Test invalid input (not a dict)
        invalid_input = "not a dict"
        assert agent.validate_input(invalid_input) == False
        
        # Test empty input
        empty_input = {}
        assert agent.validate_input(empty_input) == True  # Empty dict is valid
    
    def test_base_agent_status(self):
        """Test base agent status reporting"""
        agent = BaseAgent("test_agent")
        status = agent.get_status()
        
        assert status["agent_name"] == "test_agent"
        assert status["initialized"] == False
        assert status["execution_count"] == 0
        assert status["error_count"] == 0
        assert status["status"] == "not_initialized"

class TestScriptSummarizerAgent:
    """Test cases for ScriptSummarizerAgent"""
    
    @pytest.fixture
    def script_agent(self):
        """Create script summarizer agent for testing"""
        return ScriptSummarizerAgent()
    
    @pytest.mark.asyncio
    async def test_script_agent_initialization(self, script_agent):
        """Test script agent initialization"""
        with patch.object(script_agent, '_initialize_llm', new_callable=AsyncMock):
            await script_agent.initialize()
            assert script_agent.is_initialized
    
    def test_script_preprocessing(self, script_agent, sample_movie_script):
        """Test script text preprocessing"""
        processed = script_agent._preprocess_script(sample_movie_script)
        
        assert "scenes" in processed
        assert "characters" in processed
        assert "dialogue_lines" in processed
        assert "action_lines" in processed
        assert len(processed["characters"]) > 0
    
    def test_character_extraction(self, script_agent, sample_movie_script):
        """Test character extraction from script"""
        characters = script_agent._extract_characters(sample_movie_script)
        
        assert "JOHN" in characters
        assert "SARAH" in characters
        assert len(characters) >= 2
    
    def test_scene_detection(self, script_agent, sample_movie_script):
        """Test scene detection"""
        scenes = script_agent._detect_scenes(sample_movie_script)
        
        assert len(scenes) >= 2  # Should detect EXT. and INT. scenes
        assert any("EXT." in scene for scene in scenes)
        assert any("INT." in scene for scene in scenes)
    
    @pytest.mark.asyncio
    async def test_script_execution(self, script_agent, sample_movie_script, mock_llm_response):
        """Test script analysis execution"""
        input_data = {
            "script_text": sample_movie_script,
            "metadata": {"title": "Test Script"}
        }
        
        with patch.object(script_agent, '_initialize_llm', new_callable=AsyncMock):
            with patch.object(script_agent, '_call_llm', new_callable=AsyncMock, return_value=mock_llm_response):
                await script_agent.initialize()
                result = await script_agent.execute(input_data)
                
                assert "summary" in result
                assert "characters" in result
                assert "structure" in result
                assert "analysis" in result

class TestGenreClassificationAgent:
    """Test cases for GenreClassificationAgent"""
    
    @pytest.fixture
    def genre_agent(self):
        """Create genre classification agent for testing"""
        return GenreClassificationAgent()
    
    @pytest.mark.asyncio
    async def test_genre_agent_initialization(self, genre_agent):
        """Test genre agent initialization"""
        with patch('sentence_transformers.SentenceTransformer'):
            await genre_agent.initialize()
            assert genre_agent.is_initialized
    
    def test_text_preprocessing(self, genre_agent, sample_movie_script):
        """Test text preprocessing for genre classification"""
        processed = genre_agent._preprocess_text(sample_movie_script)
        
        assert isinstance(processed, str)
        assert len(processed) > 0
        # Should remove script formatting
        assert "FADE IN:" not in processed
        assert "EXT." not in processed
    
    def test_feature_extraction(self, genre_agent, sample_movie_script):
        """Test feature extraction"""
        features = genre_agent._extract_features(sample_movie_script)
        
        assert "word_count" in features
        assert "avg_sentence_length" in features
        assert "character_count" in features
        assert features["word_count"] > 0
    
    @pytest.mark.asyncio
    async def test_genre_classification_execution(self, genre_agent, mock_genre_classification):
        """Test genre classification execution"""
        input_data = {
            "text_content": "A romantic story about two people who meet and fall in love",
            "metadata": {}
        }
        
        with patch('sentence_transformers.SentenceTransformer'):
            with patch.object(genre_agent, '_classify_with_model', new_callable=AsyncMock, return_value=mock_genre_classification):
                await genre_agent.initialize()
                result = await genre_agent.execute(input_data)
                
                assert "primary_genre" in result
                assert "secondary_genres" in result
                assert "confidence_scores" in result

class TestMarketingRecommendationAgent:
    """Test cases for MarketingRecommendationAgent"""
    
    @pytest.fixture
    def marketing_agent(self):
        """Create marketing recommendation agent for testing"""
        return MarketingRecommendationAgent()
    
    @pytest.mark.asyncio
    async def test_marketing_agent_initialization(self, marketing_agent):
        """Test marketing agent initialization"""
        with patch('transformers.pipeline'):
            await marketing_agent.initialize()
            assert marketing_agent.is_initialized
    
    def test_text_preprocessing(self, marketing_agent, sample_social_media_posts):
        """Test social media text preprocessing"""
        processed = marketing_agent._preprocess_social_media_text(sample_social_media_posts[0])
        
        assert isinstance(processed, str)
        # Should clean hashtags, mentions, etc.
        original_post = sample_social_media_posts[0]
        if "#" in original_post:
            assert "#" not in processed or len(processed) < len(original_post)
    
    def test_sentiment_analysis(self, marketing_agent, sample_social_media_posts, mock_sentiment_analysis):
        """Test sentiment analysis"""
        with patch.object(marketing_agent, 'sentiment_analyzer', Mock()):
            with patch.object(marketing_agent, '_analyze_sentiment_batch', return_value=mock_sentiment_analysis):
                result = marketing_agent._analyze_sentiment_batch(sample_social_media_posts)
                
                assert "overall_sentiment" in result
                assert "percentages" in result
                assert "emotion_analysis" in result
    
    def test_keyword_extraction(self, marketing_agent, sample_social_media_posts):
        """Test keyword extraction from social media posts"""
        keywords = marketing_agent._extract_keywords(sample_social_media_posts)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        # Should extract relevant movie-related keywords
        assert any(keyword in ["movie", "amazing", "love", "performance"] for keyword in keywords)
    
    @pytest.mark.asyncio
    async def test_marketing_execution(self, marketing_agent, sample_social_media_posts, mock_sentiment_analysis):
        """Test marketing analysis execution"""
        input_data = {
            "social_media_data": sample_social_media_posts,
            "metadata": {"title": "Test Movie"}
        }
        
        with patch('transformers.pipeline'):
            with patch.object(marketing_agent, '_analyze_sentiment_batch', return_value=mock_sentiment_analysis):
                await marketing_agent.initialize()
                result = await marketing_agent.execute(input_data)
                
                assert "sentiment_analysis" in result
                assert "key_themes" in result
                assert "recommendations" in result
                assert "data_summary" in result

class TestAgentOrchestrator:
    """Test cases for AgentOrchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create agent orchestrator for testing"""
        return AgentOrchestrator()
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        with patch.object(orchestrator.agents["script_summarizer"], 'initialize', new_callable=AsyncMock):
            with patch.object(orchestrator.agents["genre_classifier"], 'initialize', new_callable=AsyncMock):
                with patch.object(orchestrator.agents["marketing_agent"], 'initialize', new_callable=AsyncMock):
                    await orchestrator.initialize()
                    assert orchestrator.is_initialized
    
    @pytest.mark.asyncio
    async def test_orchestrator_content_analysis(self, orchestrator, sample_movie_script, sample_social_media_posts):
        """Test complete content analysis"""
        content_data = {
            "script_text": sample_movie_script,
            "social_media_data": sample_social_media_posts,
            "metadata": {"title": "Test Movie"}
        }
        
        mock_script_result = {"summary": {"plot": "Test plot"}, "characters": ["JOHN", "SARAH"]}
        mock_genre_result = {"primary_genre": {"genre": "Drama", "confidence": 0.85}}
        mock_marketing_result = {"sentiment_analysis": {"overall_sentiment": "positive"}}
        
        with patch.object(orchestrator, '_run_script_analysis', new_callable=AsyncMock, return_value=mock_script_result):
            with patch.object(orchestrator, '_run_genre_classification', new_callable=AsyncMock, return_value=mock_genre_result):
                with patch.object(orchestrator, '_run_marketing_analysis', new_callable=AsyncMock, return_value=mock_marketing_result):
                    await orchestrator.initialize()
                    result = await orchestrator.analyze_content(content_data)
                    
                    assert "analysis_id" in result
                    assert "timestamp" in result
                    assert "content_summary" in result
                    assert "individual_results" in result
                    assert "cross_agent_insights" in result
                    assert "confidence_scores" in result
                    assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_orchestrator_status(self, orchestrator):
        """Test orchestrator status reporting"""
        with patch.object(orchestrator.agents["script_summarizer"], 'get_status', return_value={"initialized": True, "status": "ready"}):
            with patch.object(orchestrator.agents["genre_classifier"], 'get_status', return_value={"initialized": True, "status": "ready"}):
                with patch.object(orchestrator.agents["marketing_agent"], 'get_status', return_value={"initialized": True, "status": "ready"}):
                    orchestrator.is_initialized = True
                    status = await orchestrator.get_agent_status()
                    
                    assert "orchestrator_initialized" in status
                    assert "agents" in status
                    assert "cache_size" in status
                    assert "active_tasks" in status
    
    @pytest.mark.asyncio
    async def test_orchestrator_cleanup(self, orchestrator):
        """Test orchestrator cleanup"""
        with patch.object(orchestrator.agents["script_summarizer"], 'cleanup', new_callable=AsyncMock):
            with patch.object(orchestrator.agents["genre_classifier"], 'cleanup', new_callable=AsyncMock):
                with patch.object(orchestrator.agents["marketing_agent"], 'cleanup', new_callable=AsyncMock):
                    orchestrator.is_initialized = True
                    await orchestrator.cleanup()
                    assert not orchestrator.is_initialized

class TestAgentIntegration:
    """Integration tests for multiple agents working together"""
    
    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self, sample_movie_script, sample_social_media_posts, sample_content_metadata):
        """Test complete analysis pipeline with all agents"""
        orchestrator = AgentOrchestrator()
        
        content_data = {
            "script_text": sample_movie_script,
            "social_media_data": sample_social_media_posts,
            "metadata": sample_content_metadata
        }
        
        # Mock all agent responses
        mock_responses = {
            "script_analysis": {
                "summary": {"plot": "A writer's journey", "themes": ["persistence"]},
                "characters": ["JOHN", "SARAH"],
                "structure": {"scenes": 2, "pacing": "Moderate"}
            },
            "genre_classification": {
                "primary_genre": {"genre": "Drama", "confidence": 0.85},
                "secondary_genres": [{"genre": "Romance", "confidence": 0.15}]
            },
            "marketing_analysis": {
                "sentiment_analysis": {"overall_sentiment": "mixed"},
                "key_themes": ["movie", "amazing", "love"],
                "recommendations": {"campaign_themes": ["Quality", "Emotion"]}
            }
        }
        
        with patch.object(orchestrator, '_run_script_analysis', new_callable=AsyncMock, return_value=mock_responses["script_analysis"]):
            with patch.object(orchestrator, '_run_genre_classification', new_callable=AsyncMock, return_value=mock_responses["genre_classification"]):
                with patch.object(orchestrator, '_run_marketing_analysis', new_callable=AsyncMock, return_value=mock_responses["marketing_analysis"]):
                    await orchestrator.initialize()
                    result = await orchestrator.analyze_content(content_data)
                    
                    # Verify complete analysis structure
                    assert "analysis_id" in result
                    assert "individual_results" in result
                    assert len(result["individual_results"]) == 3
                    assert "script_analysis" in result["individual_results"]
                    assert "genre_classification" in result["individual_results"]
                    assert "marketing_analysis" in result["individual_results"]
                    
                    # Verify cross-agent insights were generated
                    assert "cross_agent_insights" in result
                    assert "confidence_scores" in result
                    assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_error_handling_in_pipeline(self, sample_movie_script):
        """Test error handling when one agent fails"""
        orchestrator = AgentOrchestrator()
        
        content_data = {
            "script_text": sample_movie_script,
            "metadata": {}
        }
        
        # Mock one agent to fail
        with patch.object(orchestrator, '_run_script_analysis', side_effect=Exception("Script analysis failed")):
            with patch.object(orchestrator, '_run_genre_classification', new_callable=AsyncMock, return_value={"primary_genre": {"genre": "Drama", "confidence": 0.8}}):
                await orchestrator.initialize()
                result = await orchestrator.analyze_content(content_data)
                
                # Should still return results from successful agents
                assert "individual_results" in result
                assert "genre_classification" in result["individual_results"]
                # Failed agent should have error recorded
                assert "script_analysis" in result["individual_results"]
                assert "error" in result["individual_results"]["script_analysis"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
