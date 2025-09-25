"""Application configuration management."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(default=True, env="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="langsmith-demo", env="LANGCHAIN_PROJECT")
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Application Configuration
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    vectorstore_path: str = Field(default="./data/vectorstore", env="VECTORSTORE_PATH")
    
    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    
    # JWT Configuration
    jwt_secret: str = Field(default="jwt-secret-key", env="JWT_SECRET")
    jwt_issuer: str = Field(default="eu-ai-act-api", env="JWT_ISSUER")
    jwt_audience: str = Field(default="eu-ai-act-users", env="JWT_AUDIENCE")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    
    # User Configuration
    users_config: Optional[str] = Field(default=None, env="USERS_CONFIG")
    
    # Observability Configuration
    otlp_endpoint: Optional[str] = Field(default=None, env="OTLP_ENDPOINT")
    prometheus_port: int = Field(default=8001, env="PROMETHEUS_PORT")
    
    # Monitoring Configuration
    grafana_password: str = Field(default="admin", env="GRAFANA_PASSWORD")
    
    # API Configuration
    api_title: str = "EU AI Act Compliance RAG API"
    api_version: str = "1.0.0"
    api_description: str = "Production-grade RAG API with authentication, rate limiting, and observability"
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
