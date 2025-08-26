"""Configuration settings for the Agentic AI Research Assistant."""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import tempfile

class ModelProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Core API Keys
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    groq_api_key: Optional[str] = Field(default=None)
    
    # Local LLM Configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3")
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/app.db")
    vector_db_path: str = Field(default="./data/vector_db")
    
    # Security
    secret_key: str = Field(default="dev-secret-key")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # Model Configuration
    default_model_provider: ModelProvider = Field(default=ModelProvider.OLLAMA)
    default_model_name: str = Field(default="llama3")
    
    # Application Settings
    app_name: str = Field(default="AgenTech Research Hub")
    app_version: str = Field(default="1.0.0")
    app_description: str = Field(default="Advanced Multi-Agent Research Platform")
    log_level: str = Field(default="INFO")
    max_workers: int = Field(default=4)
    enable_web_search: bool = Field(default=True)
    enable_file_processing: bool = Field(default=True)
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }

@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    name: str
    role: str
    goal: str
    backstory: str
    model_provider: ModelProvider = ModelProvider.OLLAMA
    model_name: str = "llama3"
    temperature: float = 0.7
    max_tokens: int = 4000
    tools: List[str] = field(default_factory=list)
    
@dataclass 
class ResearchConfig:
    """Configuration for research operations."""
    max_sources: int = 10
    max_depth: int = 3
    timeout_seconds: int = 300
    parallel_searches: int = 3
    quality_threshold: float = 0.7
    
@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""
    max_iterations: int = 10
    retry_attempts: int = 3
    checkpoint_interval: int = 5
    enable_human_feedback: bool = False
    
# Predefined agent configurations
AGENT_CONFIGS = {
    "researcher": AgentConfig(
        name="Research Specialist",
        role="Senior Research Analyst", 
        goal="Conduct comprehensive research on given topics using multiple sources",
        backstory="You are an experienced research analyst with expertise in gathering, analyzing, and synthesizing information from diverse sources.",
        tools=["web_search", "academic_search", "document_analysis"]
    ),
    "analyst": AgentConfig(
        name="Data Analyst",
        role="Data Analysis Expert",
        goal="Analyze and interpret research findings to extract meaningful insights", 
        backstory="You are a skilled data analyst who excels at finding patterns, trends, and insights in complex information.",
        tools=["data_analysis", "statistical_tools", "visualization"]
    ),
    "writer": AgentConfig(
        name="Content Writer", 
        role="Technical Writer",
        goal="Create clear, comprehensive reports and documentation",
        backstory="You are a professional technical writer skilled at presenting complex information in clear, accessible formats.",
        tools=["document_generation", "formatting", "editing"]
    ),
    "reviewer": AgentConfig(
        name="Quality Reviewer",
        role="Quality Assurance Specialist", 
        goal="Review and validate research outputs for accuracy and completeness",
        backstory="You are a meticulous reviewer with expertise in fact-checking and quality assurance.",
        tools=["fact_checking", "validation", "quality_assessment"]
    )
}

# Global settings instance
settings = Settings()

def get_model_config(provider: ModelProvider = None, model_name: str = None) -> Dict[str, Any]:
    """Get model configuration for the specified provider."""
    provider = provider or settings.default_model_provider
    model_name = model_name or settings.default_model_name
    
    config = {
        "provider": provider,
        "model": model_name,
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    if provider == ModelProvider.OPENAI:
        config["api_key"] = settings.openai_api_key
    elif provider == ModelProvider.ANTHROPIC:
        config["api_key"] = settings.anthropic_api_key
    elif provider == ModelProvider.GROQ:
        config["api_key"] = settings.groq_api_key
    elif provider == ModelProvider.OLLAMA:
        config["base_url"] = settings.ollama_base_url
        
    return config

def ensure_data_directories():
    """Ensure all required data directories exist."""
    directories = [
        Path(settings.vector_db_path),
        Path("./data/logs"),
        Path("./data/cache"),
        Path("./data/outputs"),
        Path("./data/checkpoints")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_temp_dir() -> str:
    """Get temporary directory for processing."""
    temp_dir = Path(tempfile.gettempdir()) / "agentic_ai"
    temp_dir.mkdir(exist_ok=True)
    return str(temp_dir)

# Initialize data directories
ensure_data_directories()

# Default research queries for demo mode
DEFAULT_RESEARCH_QUERIES = [
    "Latest developments in artificial intelligence and machine learning",
    "Impact of quantum computing on cybersecurity",
    "Sustainable energy solutions for 2024",
    "Future of blockchain technology in finance",
    "Climate change adaptation strategies for coastal cities",
    "Advances in gene therapy for rare diseases",
    "The role of AI in space exploration missions"
]

# Research query categories
RESEARCH_CATEGORIES = {
    "technology": [
        "Latest developments in quantum computing",
        "AI ethics and responsible development", 
        "Blockchain applications beyond cryptocurrency"
    ],
    "health": [
        "Personalized medicine and genomics",
        "Mental health technology solutions",
        "Telemedicine adoption and effectiveness" 
    ],
    "environment": [
        "Carbon capture technology advances",
        "Sustainable agriculture practices",
        "Ocean cleanup and marine conservation"
    ],
    "business": [
        "Future of remote work and digital nomadism",
        "Impact of automation on employment",
        "Sustainable business models for 2025"
    ]
}
