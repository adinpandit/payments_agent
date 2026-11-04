from functools import lru_cache
from pathlib import Path
from psycopg.conninfo import make_conninfo
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

    @property
    def database_url(self)->str:
        # make_conninfo quotes/escapes special characters (e.g. "@", spaces, quotes) in credentials.
        return make_conninfo(
            host = self.POSTGRES_HOST,
            port = self.POSTGRES_PORT,
            dbname = self.POSTGRES_DB,
            user = self.POSTGRES_USER,
            password = self.POSTGRES_PASSWORD,
        )

@lru_cache
def get_settings()->Settings:
    return Settings()

settings = get_settings()