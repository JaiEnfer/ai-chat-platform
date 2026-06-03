import os
from urllib.parse import urlsplit

from pydantic import field_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


def is_railway_runtime() -> bool:
    railway_markers = (
        "RAILWAY_PROJECT_ID",
        "RAILWAY_ENVIRONMENT_ID",
        "RAILWAY_SERVICE_ID",
        "RAILWAY_DEPLOYMENT_ID",
        "RAILWAY_PRIVATE_DOMAIN",
        "RAILWAY_PUBLIC_DOMAIN",
    )

    return any(os.getenv(marker) for marker in railway_markers)


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

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        hostname = urlsplit(value).hostname

        if is_railway_runtime() and hostname in {"localhost", "127.0.0.1"}:
            raise ValueError(
                "DATABASE_URL points to localhost inside Railway. "
                "Attach a Railway PostgreSQL service or set DATABASE_URL to a real database."
            )

        return value

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        if is_railway_runtime():
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )

        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
