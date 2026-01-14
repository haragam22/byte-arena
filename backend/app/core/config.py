from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    DATABASE_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    SESSION_SECRET: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    BACKEND_BASE_URL: str

    class Config:
        env_file = ROOT_DIR / ".env"
        env_file_encoding = "utf-8"
        extra = "forbid"   # keep this strict (GOOD)

settings = Settings()
