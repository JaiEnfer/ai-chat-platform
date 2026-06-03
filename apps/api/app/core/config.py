from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Berlin AI Chatbot Platform"
    environment: str = "local"
    api_prefix: str = "/api"
    database_url: str

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value

        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value[len("postgres://") :]

        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value[len("postgresql://") :]

        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
