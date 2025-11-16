"""
Configuration settings for the Background Removal API
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    app_name: str = "Background Removal API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Replicate Configuration
    replicate_api_token: str
    replicate_model: str = "851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc"
    
    # Security
    api_key_header: str = "X-RapidAPI-Proxy-Secret"
    rapidapi_key_header: str = "X-RapidAPI-Key"
    allowed_api_keys: Optional[str] = None  # Comma-separated list of allowed keys
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_default: str = "100/hour"
    rate_limit_free_tier: str = "50/day"
    rate_limit_pro_tier: str = "1000/day"
    rate_limit_ultra_tier: str = "10000/day"
    
    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds
    
    # File Validation
    max_image_size_mb: int = 10
    allowed_image_formats: list = ["jpg", "jpeg", "png", "webp", "gif"]
    
    # Webhook Configuration
    webhook_enabled: bool = True
    webhook_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_requests: bool = True
    
    # CORS
    cors_origins: list = ["*"]
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

