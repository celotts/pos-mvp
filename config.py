import sys

from pydantic import EmailStr, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    # Credenciales para el primer superusuario
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

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
    print("\n❌ Error crítico de configuración:")
    print("Faltan o son inválidas las siguientes variables en tu archivo .env:")
    for error in e.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        print(f"   • {field}: {error['msg']}")
    print("\nPor favor, actualiza tu archivo .env y vuelve a iniciar la aplicación.\n")
    sys.exit(1)
