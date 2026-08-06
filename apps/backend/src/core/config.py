# ============================================================
# CodeWhisper PR - Configuration
# ============================================================

from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, field_validator


class Settings(BaseSettings):
    """Application settings."""

    # App
    APP_NAME: str = "CodeWhisper PR Backend"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    VERSION: str = "1.0.0"
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    BCRYPT_ROUNDS: int = 12

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://codewhisper:codewhisper123@localhost:5432/codewhisper"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600
    REDIS_SESSION_TTL: int = 86400

    # Paritok
    PARITOK_API_KEY: Optional[str] = None
    PARITOK_BASE_URL: str = "http://localhost:8080"
    PARITOK_MODEL: str = "paritok-4b-v1"
    PARITOK_HOSTED_GPU_URL: Optional[str] = None

    # LLM
    LLM_PROVIDER: str = "openai"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_MAX_TOKENS: int = 4000
    LLM_TEMPERATURE: float = 0.7
    LLM_BASE_URL: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    # Allowed hosts
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]

    # Git
    GIT_CLONE_DIRECTORY: str = "/tmp/codewhisper-repos"
    GIT_MAX_FILE_SIZE: int = 1048576

    # Token Optimization
    TOKEN_OPTIMIZATION_ENABLED: bool = True
    TOKEN_OPTIMIZATION_THRESHOLD: float = 0.75
    TOKEN_SAVINGS_TARGET: float = 0.74
    MAX_CONTEXT_TOKENS: int = 4096
    MIN_OPTIMIZATION_TOKENS: int = 100

    # Features
    ENABLE_ANALYTICS: bool = True
    ENABLE_CACHING: bool = True
    ENABLE_BACKGROUND_PROCESSING: bool = True

    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 8000

    # Host
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",
    }


settings = Settings()
