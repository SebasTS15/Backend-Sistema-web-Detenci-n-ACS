from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backend Tesis Apnea"
    app_env: str = "development"

    model_path: Path = Path(r"C:\UNIVERSIDAD\DataSetApnea\modelo_apnea_central_0-3.pth")
    model_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "DB_Sistema_Deteccion_ACS"
    db_user: str = "postgres"
    db_password: str = "Sebas15"

    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
