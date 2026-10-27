import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CourtGPT Auditor"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "courtgpt_dev_secret_key_change_in_production_394829384")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./courtgpt.db")
    
    # Knowledge Graph
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password123")
    USE_INMEMORY_KG: bool = os.getenv("USE_INMEMORY_KG", "true").lower() == "true"
    
    # Storage
    STORAGE_PATH: str = os.getenv("STORAGE_PATH", "./storage")
    
    # LLM & Embedding Providers
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "deterministic_research")
    LLM_API_KEY: Optional[str] = os.getenv("LLM_API_KEY", None)
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "tfidf_bm25_dense")
    
    # Demo Mode
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
