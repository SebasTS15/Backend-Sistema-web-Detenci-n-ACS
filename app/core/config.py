from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backend Tesis Apnea"
    app_env: str = "development"

    model_path: Path = Path(r"C:\UNIVERSIDAD\BackednTesis\modelo_resnet_apnea_central_0-7.pth")
    model_threshold: float = Field(default=0.3, ge=0.0, le=1.0)

    # Base de datos - Supabase PostgreSQL
    # Opción 1: URL de conexión completa (recomendado para Supabase)
    database_url: str | None = Field(
        default=None,
        description="URL completa de conexión PostgreSQL (ej: postgresql://user:pass@host:port/db)",
    )
    
    # Opción 2: Componentes individuales (para compatibilidad)
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "DB_Sistema_Deteccion_ACS"
    db_user: str = "postgres"
    db_password: str = "Sebas15"

    cors_origins: str = "*"

    jwt_secret_key: str = Field(
        default="CHANGE_ME_SUPER_SECRET_KEY",
        env="JWT_SECRET_KEY",
        description="Clave secreta para firmar los JWT.",
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 60

    auth_username: str = Field(
        default="admin",
        env="AUTH_USERNAME",
        description="Nombre de usuario para autenticación básica JWT.",
    )
    auth_password: str = Field(
        default="admin",
        env="AUTH_PASSWORD",
        description="Contraseña para autenticación básica JWT.",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    def get_database_url(self) -> str:
        """Retorna la URL de conexión a la base de datos."""
        if self.database_url:
            return self.database_url
        
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
