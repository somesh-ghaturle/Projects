"""
Models Package - Multi-Agent Content Analytics Platform

This package contains all data models, including Pydantic models for API validation,
database models, and data transfer objects.

Author: Content Analytics Team  
Version: 3.0.0
Last Updated: August 2025
"""

from .data_models import (
    # Enums
    AgentType,
    ContentType,
    AnalysisStatus,
    PriorityLevel,
    
    # Base Models
    BaseResponse,
    ErrorDetail,
    ErrorResponse,
    
    # Request Models
    ContentAnalysisRequest,
    BulkAnalysisRequest,
    UpdateAgentConfigRequest,
    ValidateContentRequest,
    AnalysisSearchRequest,
    
    # Response Models
    ContentAnalysisResponse,
    BulkAnalysisResponse,
    HealthStatus,
    MetricsResponse,
    ConfigurationResponse,
    ValidateContentResponse,
    AnalysisHistoryResponse,
    
    # Analysis Result Models
    ScriptAnalysisResult,
    GenreClassificationResult,
    MarketingInsightsResult,
    AnalysisResult,
    
    # Component Models
    AgentInfo,
    ContentMetadata,
    CharacterProfile,
    SceneAnalysis,
    GenreScore,
    MoodAnalysis,
    AudienceSegment,
    MarketingChannel,
    AgentStatus,
    CacheInfo,
    AgentConfigModel,
    ContentValidationResult,
    AnalysisFilter,
    AnalysisHistoryItem
)

__version__ = "3.0.0"
__author__ = "Content Analytics Team"

# Model registry for dynamic access
MODEL_REGISTRY = {
    # Request Models
    "content_analysis_request": ContentAnalysisRequest,
    "bulk_analysis_request": BulkAnalysisRequest,
    "validate_content_request": ValidateContentRequest,
    "analysis_search_request": AnalysisSearchRequest,
    "update_agent_config_request": UpdateAgentConfigRequest,
    
    # Response Models
    "content_analysis_response": ContentAnalysisResponse,
    "bulk_analysis_response": BulkAnalysisResponse,
    "health_status": HealthStatus,
    "metrics_response": MetricsResponse,
    "configuration_response": ConfigurationResponse,
    "validate_content_response": ValidateContentResponse,
    "analysis_history_response": AnalysisHistoryResponse,
    
    # Analysis Results
    "script_analysis_result": ScriptAnalysisResult,
    "genre_classification_result": GenreClassificationResult,
    "marketing_insights_result": MarketingInsightsResult,
    
    # Component Models
    "agent_info": AgentInfo,
    "content_metadata": ContentMetadata,
    "character_profile": CharacterProfile,
    "scene_analysis": SceneAnalysis,
    "genre_score": GenreScore,
    "mood_analysis": MoodAnalysis,
    "audience_segment": AudienceSegment,
    "marketing_channel": MarketingChannel,
    "agent_status": AgentStatus,
    "cache_info": CacheInfo,
    "agent_config_model": AgentConfigModel,
    "content_validation_result": ContentValidationResult,
    "analysis_filter": AnalysisFilter,
    "analysis_history_item": AnalysisHistoryItem,
    
    # Error Models
    "error_detail": ErrorDetail,
    "error_response": ErrorResponse
}

# Type mappings for agent results
AGENT_RESULT_TYPES = {
    AgentType.SCRIPT_ANALYZER: ScriptAnalysisResult,
    AgentType.GENRE_CLASSIFIER: GenreClassificationResult,
    AgentType.MARKETING_INSIGHTS: MarketingInsightsResult
}

def get_model_by_name(model_name: str):
    """
    Get model class by name.
    
    Args:
        model_name: Name of the model
    
    Returns:
        Model class or None if not found
    """
    return MODEL_REGISTRY.get(model_name.lower())

def get_result_model_for_agent(agent_type: AgentType):
    """
    Get the appropriate result model for an agent type.
    
    Args:
        agent_type: Type of agent
    
    Returns:
        Result model class
    """
    return AGENT_RESULT_TYPES.get(agent_type)

def validate_model_data(model_name: str, data: dict):
    """
    Validate data against a model schema.
    
    Args:
        model_name: Name of the model
        data: Data to validate
    
    Returns:
        Validated model instance
    
    Raises:
        ValueError: If model not found or validation fails
    """
    model_class = get_model_by_name(model_name)
    if not model_class:
        raise ValueError(f"Model '{model_name}' not found")
    
    return model_class(**data)

__all__ = [
    # Core exports from data_models
    "AgentType", "ContentType", "AnalysisStatus", "PriorityLevel",
    "BaseResponse", "ErrorDetail", "ErrorResponse",
    "ContentAnalysisRequest", "BulkAnalysisRequest", "UpdateAgentConfigRequest",
    "ValidateContentRequest", "AnalysisSearchRequest",
    "ContentAnalysisResponse", "BulkAnalysisResponse", "HealthStatus",
    "MetricsResponse", "ConfigurationResponse", "ValidateContentResponse",
    "AnalysisHistoryResponse",
    "ScriptAnalysisResult", "GenreClassificationResult", "MarketingInsightsResult",
    "AnalysisResult",
    "AgentInfo", "ContentMetadata", "CharacterProfile", "SceneAnalysis",
    "GenreScore", "MoodAnalysis", "AudienceSegment", "MarketingChannel",
    "AgentStatus", "CacheInfo", "AgentConfigModel", "ContentValidationResult",
    "AnalysisFilter", "AnalysisHistoryItem",
    
    # Package utilities
    "MODEL_REGISTRY", "AGENT_RESULT_TYPES",
    "get_model_by_name", "get_result_model_for_agent", "validate_model_data"
]
