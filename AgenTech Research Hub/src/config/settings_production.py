"""
Enhanced settings configuration for production deployment
"""

import os
from typing import Optional, List
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Settings
    app_name: str = Field(default="AgenTech Research Hub")
    app_version: str = Field(default="1.0.0")
    app_description: str = Field(default="Advanced Multi-Agent Research Platform")
    app_environment: str = Field(default="development")
    debug: bool = Field(default=True)
    log_level: str = Field(default="INFO")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    allowed_hosts: List[str] = Field(default=["*"])
    
    # Security Settings
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    cors_allowed_origins: List[str] = Field(default=["*"])
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    groq_api_key: Optional[str] = Field(default=None)
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./data/app.db")
    vector_db_path: str = Field(default="./data/vector_db")
    chroma_persist_dir: str = Field(default="./data/chroma_db")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/1")
    
    # Performance Settings
    max_workers: int = Field(default=4)
    max_concurrent_agents: int = Field(default=5)
    research_timeout_seconds: int = Field(default=300)
    max_sources_per_query: int = Field(default=20)
    workflow_retry_attempts: int = Field(default=3)
    rate_limit_per_minute: int = Field(default=60)
    
    # Feature Flags
    enable_web_scraping: bool = Field(default=True)
    enable_academic_search: bool = Field(default=True)
    enable_news_search: bool = Field(default=True)
    enable_crew_ai: bool = Field(default=True)
    enable_langgraph: bool = Field(default=True)
    enable_rate_limiting: bool = Field(default=True)
    enable_api_key_auth: bool = Field(default=False)
    enable_metrics: bool = Field(default=True)
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None)
    new_relic_license_key: Optional[str] = Field(default=None)
    
    # Search APIs
    google_search_api_key: Optional[str] = Field(default=None)
    google_cse_id: Optional[str] = Field(default=None)
    bing_search_api_key: Optional[str] = Field(default=None)
    serpapi_api_key: Optional[str] = Field(default=None)
    
    # Academic Research APIs
    semantic_scholar_api_key: Optional[str] = Field(default=None)
    arxiv_api_url: str = Field(default="http://export.arxiv.org/api/query")
    pubmed_api_key: Optional[str] = Field(default=None)
    
    # News APIs
    news_api_key: Optional[str] = Field(default=None)
    alpha_vantage_api_key: Optional[str] = Field(default=None)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            # Load environment-specific config
            env = os.getenv('APP_ENVIRONMENT', 'development')
            env_files = ['.env']
            
            if env == 'production':
                env_files.append('.env.production')
            elif env == 'staging':
                env_files.append('.env.staging')
            else:
                env_files.append('.env.development')
            
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
