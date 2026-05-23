import os
from pydantic_settings import BaseSettings
from typing import Optional

# Simple local .env file loader to populate os.environ
_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_env_path = os.path.join(_root_dir, ".env")
if os.path.exists(_env_path):
    try:
        with open(_env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    k_str = key.strip()
                    if k_str not in os.environ:
                        os.environ[k_str] = val.strip().strip('"').strip("'")
    except Exception:
        pass

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Seminar System"
    API_V1_STR: str = "/api/v1"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # Can be "openai", "gemini", or "mock"
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")
    
    # Vector DB settings
    CHROMA_PERSIST_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
        "db_persist"
    )
    
    class Config:
        case_sensitive = True

# We try to use pydantic-settings if available, or fallback to simple os.getenv loading
try:
    settings = Settings()
except Exception:
    # Fallback if pydantic-settings isn't installed yet
    class SimpleSettings:
        PROJECT_NAME = "AI Seminar System"
        API_V1_STR = "/api/v1"
        LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
        GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")
        CHROMA_PERSIST_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "db_persist")
        )
    settings = SimpleSettings()
