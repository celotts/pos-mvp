import sys

from app.utils.logger import logger
from pydantic import ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    # Configuración del proveedor de LLM
    LLM_PROVIDER: str = "ollama"  # Puede ser 'ollama', 'stub', etc.
    OLLAMA_BASE_URL: str | None = None
    LLM_MODEL: str = "llama3"

    # Clave secreta y tiempo de expiración del token en segundos
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 90000  # 25 horas por defecto

    class Config:
        # Busca el archivo .env en la raíz del proyecto
        env_file = "../../.env"
        env_file_encoding = "utf-8"


try:
    settings = Settings()
except ValidationError as e:
    logger.error("\n❌ Error crítico de configuración:")
    logger.error("Faltan o son inválidas las siguientes variables en tu archivo .env:")
    for error in e.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        logger.error(f"   • {field}: {error['msg']}")
    logger.error(
        "\nPor favor, actualiza tu archivo .env y vuelve a iniciar la aplicación.\n"
    )
    sys.exit(1)
