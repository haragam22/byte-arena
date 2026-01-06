from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]  
ENV_FILE = ROOT_DIR / ".env"

class Settings:
    DATABASE_URL = "postgresql+asyncpg://arena_user:arena_pass@localhost:5432/byte_arena"
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    BACKEND_BASE_URL: str

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
settings = Settings()
