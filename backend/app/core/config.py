import sys

from pydantic import EmailStr, PostgresDsn, ValidationError, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8", case_sensitive=False)

    # PostgreSQL connection settings from .env
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    # Assembled database URL, built from the components above
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
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_FULL_NAME: str

    # IA Settings (made optional to allow tests to run without them)
    # LLM Provider to use ('ollama', 'stub', etc.)
    LLM_PROVIDER: str = "ollama"

    OLLAMA_BASE_URL: str | None = None
    LLM_MODEL: str | None = None
    EMBEDDING_MODEL: str | None = None

    # Clave secreta y tiempo de expiración del token en segundos
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 90000  # 25 horas por defecto

    # System roles that cannot be modified or deleted.
    PROTECTED_ROLES: set[str] = {"SUPER_ADMIN", "ADMIN"}


try:
    settings = Settings()
except ValidationError as e:
    print("\n❌ Error crítico de configuración:")
    print("Faltan o son inválidas las siguientes variables en tu archivo .env:")
    for error in e.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        print(f"   • {field}: {error['msg']}")
    print("\nPor favor, actualiza tu archivo .env y vuelve a iniciar la aplicación.\n")
    sys.exit(1)
