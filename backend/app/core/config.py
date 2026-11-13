import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Frugal Coder"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "frugal-coder-super-secret-jwt-key-2026-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./frugal_coder.db")
    
    # Central Gateway (Bifrost) - Canonical unified setting
    BIFROST_URL: str = os.getenv("BIFROST_URL", os.getenv("BIFROST_BASE_URL", "http://localhost:8080")).rstrip("/")
    BIFROST_API_KEY: str = os.getenv("BIFROST_API_KEY", "")
    
    # Primary Cloud Provider (Configured in Bifrost or through Bifrost routing)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    GROQ_FAST_MODEL: str = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")
    
    # Secondary Cloud Failover Provider (e.g. OpenAI)
    SECONDARY_CLOUD_PROVIDER: str = os.getenv("SECONDARY_CLOUD_PROVIDER", "openai")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Local Inference Runtime (Exclusively for confidential repositories)
    # Supports any OpenAI-compatible runtime (llama.cpp, vLLM, LM Studio, Ollama)
    LOCAL_INFERENCE_URL: str = os.getenv("LOCAL_INFERENCE_URL", "http://localhost:11434")
    LOCAL_INFERENCE_RUNTIME: str = os.getenv("LOCAL_INFERENCE_RUNTIME", "ollama")
    LOCAL_MODEL: str = os.getenv("LOCAL_MODEL", "qwen2.5-coder-3b-instruct-q4_k_m")
    
    # Default Budget Limits ($ USD)
    DEFAULT_USER_BUDGET: float = 10.00
    DEFAULT_SESSION_BUDGET: float = 2.00
    
    # Tavily Search API
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    TAVILY_BASE_URL: str = os.getenv("TAVILY_BASE_URL", "https://api.tavily.com")
    
    # Safety Limits
    AGENT_MAX_STEPS: int = 25
    STEP_TIMEOUT_SECONDS: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
