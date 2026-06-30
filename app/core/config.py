from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost/taskflow"
    SECRET_KEY: str = "troque-isso-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_SSL: bool = False

    @field_validator("DATABASE_URL")
    @classmethod
    def normalise_db_url(cls, v: str) -> str:
        # Providers deliver postgres:// or postgresql://; asyncpg needs postgresql+asyncpg://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        # asyncpg doesn't accept ?sslmode in the URL — SSL is set via connect_args
        v = v.replace("?sslmode=require", "").replace("&sslmode=require", "")
        return v


settings = Settings()
