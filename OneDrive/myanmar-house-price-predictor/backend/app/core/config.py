#!/usr/bin/env python3
"""
Core configuration module for Myanmar House Price Predictor.

Handles environment variables, database settings, API keys, and application configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application settings
    APP_NAME: str = "Myanmar House Price Predictor"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Security settings
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # Database settings
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./myanmar_house_prices.db",
        env="DATABASE_URL"
    )
    
    # OpenRouter API settings
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        env="OPENROUTER_BASE_URL"
    )
    OPENROUTER_MODEL: str = Field(
        default="anthropic/claude-3-haiku",
        env="OPENROUTER_MODEL"
    )
    
    # ML Model settings
    MODEL_PATH: str = Field(
        default="./models",
        env="MODEL_PATH"
    )
    MODEL_RETRAIN_INTERVAL_HOURS: int = Field(default=24, env="MODEL_RETRAIN_INTERVAL_HOURS")
    
    # Data settings
    DATA_PATH: str = Field(default="./data", env="DATA_PATH")
    MAX_PREDICTION_BATCH_SIZE: int = Field(default=100, env="MAX_PREDICTION_BATCH_SIZE")
    
    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # Cache settings
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL_SECONDS")
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Feature flags
    ENABLE_AI_ENRICHMENT: bool = Field(default=True, env="ENABLE_AI_ENRICHMENT")
    ENABLE_MODEL_MONITORING: bool = Field(default=True, env="ENABLE_MODEL_MONITORING")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create necessary directories
        Path(self.MODEL_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.DATA_PATH).mkdir(parents=True, exist_ok=True)
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL for migrations."""
        return self.DATABASE_URL.replace("+aiosqlite", "")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return not self.DEBUG
    
    def get_openrouter_headers(self) -> dict:
        """Get headers for OpenRouter API requests."""
        if not self.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key not configured")
        
        return {
            "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://myanmar-house-predictor.com",
            "X-Title": "Myanmar House Price Predictor"
        }


# Global settings instance
settings = Settings()