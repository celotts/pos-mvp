from pydantic import BaseModel

from .user import UserWithRole


class Token(BaseModel):
    """Esquema OAuth2 estándar requerido por Swagger UI."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Esquema para la respuesta del token, incluyendo datos del usuario."""

    access_token: str
    token_type: str
    user: UserWithRole
