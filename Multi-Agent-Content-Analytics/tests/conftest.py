"""
Test configuration and fixtures for Multi-Agent Content Analytics
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Generator
import json
import os

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_movie_script() -> str:
    """Sample movie script text for testing"""
    return """
FADE IN:

EXT. NEW YORK CITY - DAY

The bustling streets of Manhattan. People hurry past, lost in their own worlds.

JOHN (25), a young aspiring writer, walks down the sidewalk carrying a worn laptop bag.

JOHN
(to himself)
Today's the day. I can feel it.

He stops in front of a towering office building.

INT. PUBLISHER'S OFFICE - DAY

SARAH (40s), a sharp publishing executive, sits behind a large desk.

SARAH
Mr. Johnson, I've read your manuscript.

JOHN
And?

SARAH
It's... interesting. But we're looking for something with more commercial appeal.

JOHN
(disappointed)
I understand.

SARAH
Don't give up. Keep writing.

FADE OUT.
"""

@pytest.fixture
def sample_social_media_posts() -> list:
    """Sample social media posts for testing"""
    return [
        "Just watched the new movie! Absolutely amazing! #MovieNight #Love",
        "That film was terrible. Waste of time and money. #Disappointed",
        "The acting was incredible, especially the lead performance. Great job!",
        "Not sure what the hype was about. Pretty average movie.",
        "Best movie of the year! Can't wait to see it again! #MustWatch",
        "The cinematography was stunning but the plot was confusing.",
        "Loved every minute of it! Highly recommend to everyone!",
        "Could have been better. The ending felt rushed.",
        "Amazing soundtrack and great performances all around!",
        "Not my cup of tea but I can see why others might like it."
    ]

@pytest.fixture
def sample_content_metadata() -> Dict[str, Any]:
    """Sample content metadata for testing"""
    return {
        "title": "Test Movie",
        "genre_hint": "Drama",
        "target_audience": "Adults",
        "production_year": 2024,
        "budget_range": "Low",
        "director": "Test Director",
        "studio": "Test Studio"
    }

@pytest.fixture
def sample_analysis_options() -> Dict[str, Any]:
    """Sample analysis options for testing"""
    return {
        "include_script_analysis": True,
        "include_genre_classification": True,
        "include_marketing_analysis": True,
        "detailed_insights": True,
        "cache_results": False  # Disable caching in tests
    }

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Test configuration"""
    return {
        "database": {
            "type": "sqlite",
            "path": ":memory:"  # Use in-memory SQLite for tests
        },
        "agents": {
            "script_summarizer": {
                "model_name": "test_model",
                "max_tokens": 1000
            },
            "genre_classifier": {
                "algorithm": "logistic",
                "confidence_threshold": 0.5
            },
            "marketing_agent": {
                "sentiment_model": "test_sentiment",
                "max_posts": 100
            }
        },
        "api": {
            "host": "localhost",
            "port": 8000,
            "debug": True
        },
        "logging": {
            "level": "DEBUG",
            "enable_console": True,
            "enable_file": False  # Disable file logging in tests
        }
    }

@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing"""
    return {
        "summary": {
            "plot": "A young writer tries to get his manuscript published in New York City.",
            "themes": ["Perseverance", "Dreams", "Rejection"],
            "tone": "Inspirational"
        },
        "characters": [
            {"name": "JOHN", "description": "Young aspiring writer, determined"},
            {"name": "SARAH", "description": "Publishing executive, professional"}
        ],
        "structure": {
            "act_count": 1,
            "scene_count": 2,
            "pacing": "Moderate"
        },
        "analysis": {
            "estimated_runtime": "15 minutes",
            "dialogue_quality": "Good",
            "commercial_potential": "Medium"
        }
    }

@pytest.fixture
def mock_genre_classification():
    """Mock genre classification results"""
    return {
        "primary_genre": {
            "genre": "Drama",
            "confidence": 0.85
        },
        "secondary_genres": [
            {"genre": "Romance", "confidence": 0.12},
            {"genre": "Comedy", "confidence": 0.03}
        ],
        "all_probabilities": {
            "Drama": 0.85,
            "Romance": 0.12,
            "Comedy": 0.03
        },
        "classification_method": "ml_model"
    }

@pytest.fixture
def mock_sentiment_analysis():
    """Mock sentiment analysis results"""
    return {
        "overall_sentiment": "mixed",
        "percentages": {
            "positive_percent": 45.0,
            "negative_percent": 25.0,
            "neutral_percent": 30.0
        },
        "emotion_analysis": {
            "joy": 0.4,
            "anger": 0.2,
            "surprise": 0.1,
            "sadness": 0.15,
            "fear": 0.05,
            "disgust": 0.1
        },
        "confidence": 0.78
    }

class MockAgent:
    """Mock agent for testing"""
    
    def __init__(self, name: str, response_data: Dict[str, Any]):
        self.name = name
        self.response_data = response_data
        self.initialized = False
        self.execution_count = 0
    
    async def initialize(self):
        """Mock initialization"""
        self.initialized = True
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock execution"""
        self.execution_count += 1
        return self.response_data
    
    def get_status(self) -> Dict[str, Any]:
        """Mock status"""
        return {
            "initialized": self.initialized,
            "status": "ready" if self.initialized else "not_initialized",
            "execution_count": self.execution_count,
            "error_count": 0
        }
    
    async def cleanup(self):
        """Mock cleanup"""
        self.initialized = False

@pytest.fixture
def mock_script_agent(mock_llm_response):
    """Mock script summarizer agent"""
    return MockAgent("script_summarizer", mock_llm_response)

@pytest.fixture
def mock_genre_agent(mock_genre_classification):
    """Mock genre classifier agent"""
    return MockAgent("genre_classifier", mock_genre_classification)

@pytest.fixture
def mock_marketing_agent(mock_sentiment_analysis):
    """Mock marketing agent"""
    marketing_response = {
        "sentiment_analysis": mock_sentiment_analysis,
        "key_themes": ["love", "movie", "amazing", "performance"],
        "engagement_metrics": {
            "total_posts": 10,
            "avg_engagement": 0.65,
            "sentiment_distribution": mock_sentiment_analysis["percentages"]
        },
        "recommendations": {
            "campaign_themes": ["Quality Acting", "Emotional Story"],
            "target_demographics": ["18-34", "Drama Fans"],
            "immediate_actions": ["Highlight cast", "Share reviews"],
            "long_term_strategies": ["Awards campaign", "Director interviews"]
        },
        "data_summary": {
            "processed_posts": 10,
            "valid_posts": 10,
            "processing_time": 0.5
        }
    }
    return MockAgent("marketing_agent", marketing_response)

# Test data files
@pytest.fixture
def create_test_data_files(temp_dir):
    """Create test data files"""
    data_dir = temp_dir / "test_data"
    data_dir.mkdir()
    
    # Create sample script file
    script_file = data_dir / "sample_script.txt"
    with open(script_file, 'w') as f:
        f.write("""
FADE IN:

EXT. PARK - DAY

A beautiful sunny day in the park.

ALICE (20s) sits on a bench reading a book.

ALICE
What a perfect day for reading.

BOB (30s) approaches with a dog.

BOB
Excuse me, is this seat taken?

ALICE
Not at all. Please, sit.

FADE OUT.
        """)
    
    # Create sample social media data
    social_file = data_dir / "social_media.json"
    posts = [
        "Great movie! Loved every minute of it!",
        "Not impressed. Expected better.",
        "Amazing cinematography and acting!",
        "The plot was confusing but visually stunning."
    ]
    with open(social_file, 'w') as f:
        json.dump(posts, f)
    
    return data_dir

# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    # Set test environment variables
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"

def pytest_unconfigure(config):
    """Cleanup after tests"""
    # Clean up environment variables
    os.environ.pop("TESTING", None)
    os.environ.pop("LOG_LEVEL", None)
