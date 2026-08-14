from pydantic import BaseModel

from .user import User


class TokenData(BaseModel):
    """Esquema para la respuesta del token, incluyendo datos del usuario."""

    access_token: str
    token_type: str
    user: User
