# core/config.py
import sys
from pathlib import Path

from pydantic import EmailStr, PostgresDsn, ValidationError, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Inyecta las variables de entorno del contenedor si .env no está presente
        env_file=ENV_FILE_PATH if ENV_FILE_PATH.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # PostgreSQL settings
    POSTGRES_HOST: str = "pos-db"
    POSTGRES_USER: str = "product"
    POSTGRES_PASSWORD: str = "product123"
    POSTGRES_DB: str = "pos_db"
    POSTGRES_PORT: int = 5432

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )

    # Credenciales para el primer superusuario
    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@posAdmin.com"
    FIRST_SUPERUSER_PASSWORD: str = "PasswordPasAdmin123!"
    FIRST_SUPERUSER_FULL_NAME: str = "Admin"

    # IA Settings (Valores predeterminados corregidos)
    LLM_PROVIDER: str = "ollama"
    OLLAMA_BASE_URL: str = "http://host.containers.internal:11434"
    LLM_MODEL: str = "llama3.2:latest"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    EMBEDDING_DIM: int = 768  # Dimensión de nomic-embed-text

    # JWT Settings
    SECRET_KEY: str = "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 90000

    # System roles
    PROTECTED_ROLES: set[str] = {"SUPER_ADMIN", "ADMIN"}


try:
    settings = Settings()
except ValidationError as e:
    print("\n❌ Error crítico de configuración:")
    print("Faltan o son inválidas las siguientes variables en tu archivo .env:")
    for error in e.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        print(f"    • {field}: {error['msg']}")
    print("\nPor favor, actualiza tu archivo .env y vuelve a iniciar la aplicación.\n")
    sys.exit(1)
