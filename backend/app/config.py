from pathlib import Path
from pydantic_settings import BaseSettings , SettingsConfigDict


# Repository root .env (shared with docker-compose), independent of the working directory.
ROOT_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    APP_NAME:str = "Yaadi"
    APP_ENV:str = "development"
    DEBUG: bool = True

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    model_config = SettingsConfigDict(
        env_file = (ROOT_ENV_FILE, ".env"),
        env_file_encoding = "utf-8",
        extra = "ignore",
    )

settings = Settings()