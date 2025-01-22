import os
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from enum import Enum

load_dotenv()

class AppSettings(BaseSettings):
    APP_NAME: str = Field(default=os.getenv("APP_NAME", "FastAPI app"))
    APP_DESCRIPTION: str | None = Field(default=os.getenv("APP_DESCRIPTION"))
    APP_VERSION: str | None = Field(default=os.getenv("APP_VERSION"))


class JwtSettings(BaseSettings):
    SECRET_KEY: str = Field(default=os.getenv("SECRET_KEY"))
    ALGORITHM: str = Field(default=os.getenv("ALGORITHM", "HS256"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))

class PostgresSettings(BaseSettings):
    POSTGRES_USER: str = Field(default=os.getenv("POSTGRES_USER", "postgres"))
    POSTGRES_PASSWORD: str = Field(default=os.getenv("POSTGRES_PASSWORD", "postgres"))
    POSTGRES_SERVER: str = Field(default=os.getenv("POSTGRES_SERVER", "localhost"))
    POSTGRES_PORT: int = Field(default=int(os.getenv("POSTGRES_PORT", 5432)))
    POSTGRES_DB: str = Field(default=os.getenv("POSTGRES_DB", "postgres"))
    POSTGRES_SYNC_PREFIX: str = Field(default=os.getenv("POSTGRES_SYNC_PREFIX", "postgresql+psycopg2://"))
    POSTGRES_ASYNC_PREFIX: str = Field(default=os.getenv("POSTGRES_ASYNC_PREFIX", "postgresql+asyncpg://"))
    POSTGRES_URI: str = Field(default=f"{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_SERVER')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}")

class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = Field(default=os.getenv("ENVIRONMENT", EnvironmentOption.LOCAL))

class Settings(
    AppSettings,
    JwtSettings,
    PostgresSettings,
    EnvironmentSettings,
):
    pass

settings = Settings()