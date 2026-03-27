"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the FlowForge API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://flowforge:flowforge@localhost:5432/flowforge"
    SECRET_KEY: str = "change-me-in-development"
    AIRFLOW_API_URL: str = "http://airflow-apiserver:8080/api/v2"
    AIRFLOW_USERNAME: str = "airflow"
    AIRFLOW_PASSWORD: str = "airflow"
    DAGS_DIR: str = "/opt/airflow/dags"
    DEBUG: bool = False


settings = Settings()
