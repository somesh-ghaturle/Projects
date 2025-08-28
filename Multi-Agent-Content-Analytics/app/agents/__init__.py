"""
Agents Module - Multi-Agent Content Analytics Platform

This module contains specialized AI agents for content analysis:
- ScriptAnalyzerAgent: Advanced script and screenplay analysis
- GenreClassificationAgent: Intelligent genre detection and classification
- MarketingInsightsAgent: Marketing strategy and audience analysis

Author: Content Analytics Team
Version: 3.0.0
License: MIT
"""

from .script_analyzer_agent import ScriptAnalyzerAgent
from .genre_classification_agent import GenreClassificationAgent
from .marketing_insights_agent import MarketingInsightsAgent

__all__ = [
    "ScriptAnalyzerAgent",
    "GenreClassificationAgent", 
    "MarketingInsightsAgent"
]

from .script_analyzer_agent import ScriptAnalyzerAgent
from .genre_classification_agent import GenreClassificationAgent
from .marketing_insights_agent import MarketingInsightsAgent

__all__ = [
    "ScriptAnalyzerAgent",
    "GenreClassificationAgent", 
    "MarketingInsightsAgent"
]

# Agent registry for dynamic loading and management
AGENT_REGISTRY = {
    "script_analyzer": ScriptAnalyzerAgent,
    "genre_classifier": GenreClassificationAgent,
    "marketing_insights": MarketingInsightsAgent
}

# Agent metadata for API documentation and UI generation
AGENT_METADATA = {
    "script_analyzer": {
        "name": "Script Analyzer",
        "description": "Comprehensive script analysis including character development, plot structure, and quality assessment",
        "capabilities": [
            "Character analysis and development tracking",
            "Scene structure and pacing analysis", 
            "Dialogue quality assessment",
            "Plot structure mapping",
            "Quality scoring and recommendations"
        ],
        "input_types": ["screenplay", "script", "dialogue"],
        "output_format": "detailed_analysis"
    },
    "genre_classifier": {
        "name": "Genre Classifier",
        "description": "AI-powered genre detection and content classification with mood analysis",
        "capabilities": [
            "Multi-genre classification",
            "Confidence scoring",
            "Mood and tone analysis",
            "Content rating assessment",
            "Audience targeting"
        ],
        "input_types": ["text", "script", "synopsis"],
        "output_format": "classification_report"
    },
    "marketing_insights": {
        "name": "Marketing Insights",
        "description": "Strategic marketing analysis and audience insights generation",
        "capabilities": [
            "Target audience identification",
            "Marketing hook generation",
            "Channel strategy recommendations",
            "Competitive analysis",
            "Budget allocation guidance"
        ],
        "input_types": ["content", "script", "synopsis"],
        "output_format": "marketing_strategy"
    }
}
