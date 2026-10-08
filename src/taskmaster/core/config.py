"""Modulo di configurazione globale dell'applicazione basato su Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurazione applicativa caricabile da variabili d'ambiente o file .env."""

    app_name: str = "TaskMaster API"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./taskmaster.db"

    # Sicurezza & JWT
    jwt_secret_key: str = "insecure-default-change-me-in-production-env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 ore

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Restituisce l'istanza singleton cachata delle impostazioni."""
    return Settings()
