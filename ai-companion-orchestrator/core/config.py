"""
Application configuration management using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "ai-companion-orchestrator"
    app_env: str = Field(default="development", pattern="^(development|staging|production)$")
    app_debug: bool = True
    app_secret_key: str = Field(..., min_length=32)
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Database
    database_url: str
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    
    # JWT Authentication
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # LLM Configuration
    llm_provider: str = "ollama"  # "ollama" or "anthropic"
    
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    
    # Anthropic Claude (fallback)
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # OpenAI (Whisper)
    openai_api_key: str
    whisper_model: str = "whisper-1"
    
    # ElevenLabs
    elevenlabs_api_key: str
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"
    
    # RAG Configuration
    rag_chunk_size: int = 500
    rag_chunk_overlap: int = 50
    rag_embedding_provider: str = "sentence-transformers"  # "openai" or "sentence-transformers"
    rag_embedding_model: str = "all-MiniLM-L6-v2"  # For sentence-transformers: all-MiniLM-L6-v2, all-mpnet-base-v2
    rag_openai_embedding_model: str = "text-embedding-3-small"  # For OpenAI provider
    rag_embedding_dimension: int = 384  # 384 for MiniLM, 768 for mpnet, 1536 for OpenAI small
    rag_top_k: int = 5
    rag_score_threshold: float = 0.4  # Lower threshold for sentence-transformers (0.4-0.6 typical range)
    rag_vector_store_path: str = "data/vector_store"
    rag_similarity_metric: str = "cosine"
    
    # Feature Flags
    enable_analytics: bool = True
    enable_multi_device: bool = True
    enable_offline_mode: bool = True
    enable_fine_tuning: bool = False
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
