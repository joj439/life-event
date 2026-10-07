import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine candidate .env locations
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env" if (BASE_DIR / ".env").exists() else ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "LifeEvent API"
    PROJECT_VERSION: str = "1.0.0"
    TAGLINE: str = "Government services, organized around your life."
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = [
        "*",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # OpenRouter LLM Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "openrouter/free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Optional Gemini Legacy Key
    GEMINI_API_KEY: str = ""

    # MySQL Database Configuration
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "lifeevent_db"
    USE_MYSQL: bool = False

    @property
    def DATABASE_URL(self) -> str:
        import urllib.parse
        encoded_pwd = urllib.parse.quote_plus(self.MYSQL_PASSWORD) if self.MYSQL_PASSWORD else ""
        if encoded_pwd:
            return f"mysql+pymysql://{self.MYSQL_USER}:{encoded_pwd}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
        return f"mysql+pymysql://{self.MYSQL_USER}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

settings = Settings()
