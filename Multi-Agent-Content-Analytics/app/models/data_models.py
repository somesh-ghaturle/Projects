"""
Data Models Module - Multi-Agent Content Analytics Platform

This module defines Pydantic models for request/response validation,
data serialization, and API documentation. It provides type-safe
data structures for all platform operations.

Author: Content Analytics Team  
Version: 3.0.0
Last Updated: August 2025
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
import hashlib

class AgentType(str, Enum):
    """Enumeration of available agent types"""
    SCRIPT_ANALYZER = "script_analyzer"
    GENRE_CLASSIFIER = "genre_classifier"
    MARKETING_INSIGHTS = "marketing_insights"

class ContentType(str, Enum):
    """Enumeration of supported content types"""
    SCREENPLAY = "screenplay"
    SCRIPT = "script"
    DIALOGUE = "dialogue"
    SYNOPSIS = "synopsis"
    TREATMENT = "treatment"
    GENERAL_TEXT = "general_text"

class AnalysisStatus(str, Enum):
    """Enumeration of analysis status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class PriorityLevel(str, Enum):
    """Priority levels for analysis requests"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Base Models

class BaseResponse(BaseModel):
    """Base response model with common fields"""
    success: bool = Field(..., description="Whether the operation was successful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    request_id: Optional[str] = Field(None, description="Unique request identifier")

class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    suggestion: Optional[str] = Field(None, description="Suggested resolution")

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = Field(False, description="Always false for error responses")
    error: ErrorDetail = Field(..., description="Error details")

# Request Models

class AnalysisRequest(BaseModel):
    """Simplified analysis request model for API compatibility"""
    content: str = Field(min_length=1, description="Content to analyze")
    agent: AgentType = Field(description="Agent type to use for analysis")
    content_type: Optional[ContentType] = Field(default=ContentType.GENERAL_TEXT, description="Content type")
    priority: Optional[PriorityLevel] = Field(default=PriorityLevel.MEDIUM, description="Analysis priority")
    cache_enabled: bool = Field(default=True, description="Enable caching")
    preprocessing_enabled: bool = Field(default=True, description="Enable preprocessing")

class AnalysisResponse(BaseResponse):
    """Simplified analysis response model for API compatibility"""
    result: Dict[str, Any] = Field(description="Analysis result data")
    agent: str = Field(description="Agent used for analysis")
    processing_time: float = Field(description="Processing time in seconds")
    cached: bool = Field(default=False, description="Whether result was cached")
    timestamp: str = Field(description="Analysis timestamp")

class HealthResponse(BaseResponse):
    """Health check response model"""
    status: str = Field(description="System health status")
    version: str = Field(description="Platform version")
    agents: Dict[str, Any] = Field(description="Agent status information")
    cache_stats: Dict[str, Any] = Field(description="Cache statistics")
    uptime_seconds: float = Field(description="System uptime in seconds")

class BulkAnalysisResponse(BaseResponse):
    """Bulk analysis response model"""
    results: List[Dict[str, Any]] = Field(description="Analysis results")
    failed_items: List[Dict[str, Any]] = Field(description="Failed analysis items") 
    total_items: int = Field(description="Total items processed")
    successful_items: int = Field(description="Successfully processed items")
    processing_time: float = Field(description="Total processing time")

class ContentAnalysisRequest(BaseModel):
    """Request model for content analysis"""
    content: str = Field(
        ..., 
        min_length=10, 
        max_length=1048576,
        description="Content to analyze (10 chars to 1MB)"
    )
    agent: AgentType = Field(
        AgentType.SCRIPT_ANALYZER,
        description="Agent type to use for analysis"
    )
    content_type: Optional[ContentType] = Field(
        None,
        description="Type of content being analyzed"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional parameters for analysis"
    )
    priority: PriorityLevel = Field(
        PriorityLevel.MEDIUM,
        description="Analysis priority level"
    )
    cache_enabled: bool = Field(
        True,
        description="Whether to use cached results if available"
    )
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        """Validate content is not empty after stripping whitespace"""
        if not v.strip():
            raise ValueError('Content cannot be empty or only whitespace')
        return v.strip()
    
    @model_validator(mode='after')
    def validate_content_size(self) -> 'ContentAnalysisRequest':
        """Validate content size constraints."""
        content = self.content
        if len(content.encode('utf-8')) > self.max_content_size:
            raise ValueError(f"Content exceeds maximum size of {self.max_content_size} bytes")
        return self
    
    def get_content_hash(self) -> str:
        """Generate hash of content for caching"""
        content_bytes = self.content.encode('utf-8')
        return hashlib.sha256(content_bytes).hexdigest()[:16]

class BulkAnalysisRequest(BaseModel):
    """Request model for bulk content analysis"""
    requests: List[ContentAnalysisRequest] = Field(
        ...,
        min_items=1,
        max_items=10,
        description="List of analysis requests (max 10)"
    )
    parallel_processing: bool = Field(
        True,
        description="Whether to process requests in parallel"
    )
    
    @field_validator('requests')
    @classmethod
    def validate_unique_content(cls, v):
        """Ensure no duplicate content in bulk request"""
        content_hashes = set()
        for request in v:
            content_hash = request.get_content_hash()
            if content_hash in content_hashes:
                raise ValueError('Duplicate content found in bulk request')
            content_hashes.add(content_hash)
        return v

# Response Models

class AgentInfo(BaseModel):
    """Information about the agent that performed analysis"""
    name: str = Field(..., description="Agent name")
    version: str = Field(..., description="Agent version")
    processing_time: float = Field(..., description="Processing time in seconds")
    capabilities: Optional[List[str]] = Field(None, description="Agent capabilities")

class ContentMetadata(BaseModel):
    """Metadata about the analyzed content"""
    content_type: str = Field(..., description="Detected or specified content type")
    word_count: int = Field(..., description="Number of words in content")
    character_count: int = Field(..., description="Number of characters in content")
    estimated_reading_time: Optional[str] = Field(None, description="Estimated reading time")
    language: Optional[str] = Field("en", description="Detected language")
    complexity_score: Optional[float] = Field(None, description="Content complexity score")

# Script Analyzer Models

class CharacterProfile(BaseModel):
    """Character analysis profile"""
    name: str = Field(..., description="Character name")
    dialogue_lines: int = Field(..., description="Number of dialogue lines")
    scene_appearances: int = Field(..., description="Number of scene appearances")
    emotional_range: List[str] = Field(..., description="Detected emotional range")
    character_importance: str = Field(..., description="Character importance level")
    development_arc: str = Field(..., description="Character development arc")
    key_phrases: List[str] = Field(..., description="Memorable dialogue phrases")
    relationship_network: Optional[List[str]] = Field(None, description="Character relationships")

class SceneAnalysis(BaseModel):
    """Scene analysis details"""
    location_name: str = Field(..., description="Scene location")
    location_type: str = Field(..., description="Interior/Exterior")
    time_of_day: str = Field(..., description="Time of day")
    estimated_duration: float = Field(..., description="Estimated scene duration")
    character_count: Optional[int] = Field(None, description="Number of characters in scene")

class ScriptAnalysisResult(BaseModel):
    """Script analyzer result model"""
    agent_info: AgentInfo
    script_metadata: ContentMetadata
    content_analysis: Dict[str, Any] = Field(..., description="Detailed content analysis")
    quality_assessment: Dict[str, Any] = Field(..., description="Quality scoring and recommendations")
    technical_metrics: Dict[str, Any] = Field(..., description="Technical analysis metrics")

# Genre Classifier Models

class GenreScore(BaseModel):
    """Genre classification score"""
    genre: str = Field(..., description="Genre name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    supporting_evidence: List[str] = Field(..., description="Supporting evidence for classification")

class MoodAnalysis(BaseModel):
    """Mood and tone analysis"""
    overall_mood: str = Field(..., description="Overall mood classification")
    emotional_intensity: str = Field(..., description="Emotional intensity level")
    tone_descriptors: List[str] = Field(..., description="Tone descriptive terms")
    emotional_range: str = Field(..., description="Emotional range description")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score (-1 to 1)")

class GenreClassificationResult(BaseModel):
    """Genre classifier result model"""
    agent_info: AgentInfo
    genre_classification: Dict[str, Any] = Field(..., description="Genre classification results")
    content_analysis: Dict[str, Any] = Field(..., description="Content analysis details")
    audience_insights: Dict[str, Any] = Field(..., description="Target audience insights")
    metadata: Dict[str, Any] = Field(..., description="Analysis metadata")
    insights_and_recommendations: Dict[str, Any] = Field(..., description="Insights and recommendations")

# Marketing Insights Models

class AudienceSegment(BaseModel):
    """Target audience segment"""
    segment: str = Field(..., description="Audience segment name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in segment targeting")
    characteristics: List[str] = Field(..., description="Segment characteristics")
    media_preferences: List[str] = Field(..., description="Preferred media channels")

class MarketingChannel(BaseModel):
    """Marketing channel recommendation"""
    channel: str = Field(..., description="Marketing channel name")
    effectiveness: float = Field(..., ge=0.0, le=1.0, description="Channel effectiveness score")
    target_segment: str = Field(..., description="Primary target segment")
    priority: str = Field(..., description="Channel priority level")
    budget_allocation: Optional[float] = Field(None, description="Recommended budget percentage")

class MarketingInsightsResult(BaseModel):
    """Marketing insights result model"""
    agent_info: AgentInfo
    audience_intelligence: Dict[str, Any] = Field(..., description="Audience analysis and insights")
    positioning_and_messaging: Dict[str, Any] = Field(..., description="Positioning and messaging strategy")
    channel_strategy: Dict[str, Any] = Field(..., description="Channel strategy recommendations")
    competitive_intelligence: Dict[str, Any] = Field(..., description="Competitive analysis")
    campaign_strategy: Dict[str, Any] = Field(..., description="Campaign development strategy")
    performance_framework: Dict[str, Any] = Field(..., description="Performance measurement framework")
    strategic_recommendations: Dict[str, Any] = Field(..., description="Strategic recommendations")
    risk_management: Dict[str, Any] = Field(..., description="Risk assessment and mitigation")

# Union type for all analysis results
AnalysisResult = Union[ScriptAnalysisResult, GenreClassificationResult, MarketingInsightsResult]

class ContentAnalysisResponse(BaseResponse):
    """Response model for content analysis"""
    success: bool = Field(True, description="Always true for successful responses")
    agent: AgentType = Field(..., description="Agent used for analysis")
    content_hash: str = Field(..., description="Hash of analyzed content")
    result: AnalysisResult = Field(..., description="Analysis results")
    cached: bool = Field(False, description="Whether result was retrieved from cache")

class BulkAnalysisResponse(BaseResponse):
    """Response model for bulk analysis"""
    success: bool = Field(True, description="Overall success status")
    results: List[ContentAnalysisResponse] = Field(..., description="Individual analysis results")
    failed_requests: List[ErrorResponse] = Field(..., description="Failed analysis requests")
    summary: Dict[str, Any] = Field(..., description="Bulk analysis summary")

# System Models

class HealthStatus(BaseModel):
    """System health status"""
    status: str = Field(..., description="Overall system status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agents: Dict[str, Dict[str, Any]] = Field(..., description="Agent status information")
    system_metrics: Optional[Dict[str, Any]] = Field(None, description="System performance metrics")

class AgentStatus(BaseModel):
    """Individual agent status"""
    name: str = Field(..., description="Agent name")
    version: str = Field(..., description="Agent version")
    enabled: bool = Field(..., description="Whether agent is enabled")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    total_requests: int = Field(0, description="Total requests processed")
    success_rate: float = Field(1.0, ge=0.0, le=1.0, description="Success rate")
    average_processing_time: float = Field(0.0, description="Average processing time")

class CacheInfo(BaseModel):
    """Cache information"""
    enabled: bool = Field(..., description="Whether caching is enabled")
    hit_rate: float = Field(0.0, ge=0.0, le=1.0, description="Cache hit rate")
    total_requests: int = Field(0, description="Total cache requests")
    cache_size: int = Field(0, description="Current cache size")
    memory_usage: Optional[str] = Field(None, description="Cache memory usage")

class MetricsResponse(BaseResponse):
    """System metrics response"""
    success: bool = Field(True)
    agents: List[AgentStatus] = Field(..., description="Agent metrics")
    cache_info: CacheInfo = Field(..., description="Cache metrics")
    system_info: Dict[str, Any] = Field(..., description="System information")

# Configuration Models

class AgentConfigModel(BaseModel):
    """Agent configuration model"""
    name: str = Field(..., description="Agent name")
    enabled: bool = Field(True, description="Whether agent is enabled")
    max_processing_time: float = Field(30.0, gt=0, description="Maximum processing time")
    memory_limit_mb: int = Field(512, gt=0, description="Memory limit in MB")
    cache_timeout: int = Field(3600, gt=0, description="Cache timeout in seconds")

class UpdateAgentConfigRequest(BaseModel):
    """Request to update agent configuration"""
    agent: AgentType = Field(..., description="Agent to configure")
    config: AgentConfigModel = Field(..., description="New configuration")

class ConfigurationResponse(BaseResponse):
    """Configuration response"""
    success: bool = Field(True)
    current_config: Dict[str, Any] = Field(..., description="Current system configuration")
    agent_configs: Dict[str, AgentConfigModel] = Field(..., description="Agent configurations")

# Validation Models

class ContentValidationResult(BaseModel):
    """Content validation result"""
    valid: bool = Field(..., description="Whether content is valid")
    issues: List[str] = Field(..., description="Validation issues found")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    estimated_processing_time: float = Field(..., description="Estimated processing time")

class ValidateContentRequest(BaseModel):
    """Request to validate content before analysis"""
    content: str = Field(..., min_length=1, max_length=1048576)
    agent: AgentType = Field(...)
    
class ValidateContentResponse(BaseResponse):
    """Content validation response"""
    success: bool = Field(True)
    validation_result: ContentValidationResult = Field(..., description="Validation results")

# Search and Filter Models

class AnalysisFilter(BaseModel):
    """Filter for analysis history"""
    agent: Optional[AgentType] = Field(None, description="Filter by agent type")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    status: Optional[AnalysisStatus] = Field(None, description="Filter by status")
    content_type: Optional[ContentType] = Field(None, description="Filter by content type")

class AnalysisSearchRequest(BaseModel):
    """Request to search analysis history"""
    filters: Optional[AnalysisFilter] = Field(None, description="Search filters")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("timestamp", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

class AnalysisHistoryItem(BaseModel):
    """Analysis history item"""
    id: str = Field(..., description="Analysis ID")
    timestamp: datetime = Field(..., description="Analysis timestamp")
    agent: AgentType = Field(..., description="Agent used")
    status: AnalysisStatus = Field(..., description="Analysis status")
    content_hash: str = Field(..., description="Content hash")
    processing_time: Optional[float] = Field(None, description="Processing time")
    cached: bool = Field(False, description="Whether result was cached")

class AnalysisHistoryResponse(BaseResponse):
    """Analysis history response"""
    success: bool = Field(True)
    items: List[AnalysisHistoryItem] = Field(..., description="History items")
    total_count: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

# Export all models
__all__ = [
    # Enums
    "AgentType", "ContentType", "AnalysisStatus", "PriorityLevel",
    
    # Base Models
    "BaseResponse", "ErrorDetail", "ErrorResponse",
    
    # Request Models
    "ContentAnalysisRequest", "BulkAnalysisRequest", "UpdateAgentConfigRequest",
    "ValidateContentRequest", "AnalysisSearchRequest",
    
    # Response Models
    "ContentAnalysisResponse", "BulkAnalysisResponse", "HealthStatus",
    "MetricsResponse", "ConfigurationResponse", "ValidateContentResponse",
    "AnalysisHistoryResponse",
    
    # Analysis Result Models
    "ScriptAnalysisResult", "GenreClassificationResult", "MarketingInsightsResult",
    "AnalysisResult",
    
    # Component Models
    "AgentInfo", "ContentMetadata", "CharacterProfile", "SceneAnalysis",
    "GenreScore", "MoodAnalysis", "AudienceSegment", "MarketingChannel",
    "AgentStatus", "CacheInfo", "AgentConfigModel", "ContentValidationResult",
    "AnalysisFilter", "AnalysisHistoryItem"
]
