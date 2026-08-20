from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Environment
    APP_ENV: str = "development"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # LLM Provider Configuration
    LLM_PROVIDER: str = "groq"
    MODEL_NAME: str = "openai/gpt-oss-120b"
    
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"

    # Hugging Face (for downloading embedding models)
    HF_TOKEN: Optional[str] = None

    # Search & Tools
    TAVILY_API_KEY: Optional[str] = None

    # Infrastructure
    DATABASE_URL: str
    REDIS_URL: str
    QDRANT_URL: str

    # Langfuse Observability
    LANGFUSE_PUBLIC_KEY: Optional[str] = None
    LANGFUSE_SECRET_KEY: Optional[str] = None
    LANGFUSE_HOST: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=False,
        extra="ignore"
    )

settings = Settings()
