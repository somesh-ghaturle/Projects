"""
Configuration management for Multi-Agent Content Analytics System
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    RELOAD: bool = Field(default=False, env="RELOAD")
    
    # Security
    SECRET_KEY: str = Field(env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database Configuration
    DATABASE_URL: str = Field(env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Vector Database
    CHROMA_DB_PATH: str = Field(default="./data/chroma_db", env="CHROMA_DB_PATH")
    CHROMA_COLLECTION_NAME: str = Field(default="content_embeddings", env="CHROMA_COLLECTION_NAME")
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    
    # External Services
    TWITTER_API_KEY: Optional[str] = Field(default=None, env="TWITTER_API_KEY")
    REDDIT_CLIENT_ID: Optional[str] = Field(default=None, env="REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET: Optional[str] = Field(default=None, env="REDDIT_CLIENT_SECRET")
    
    # Model Configuration
    DEFAULT_LLM_MODEL: str = Field(default="gpt-4-1106-preview", env="DEFAULT_LLM_MODEL")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    SENTIMENT_MODEL: str = Field(
        default="cardiffnlp/twitter-roberta-base-sentiment-latest",
        env="SENTIMENT_MODEL"
    )
    
    # Cache Settings
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    MAX_CACHE_SIZE: int = Field(default=1000, env="MAX_CACHE_SIZE")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # Monitoring
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(default=3000, env="GRAFANA_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
