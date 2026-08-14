import uuid

from core.crud_user import crud_user
from core.db import async_session_maker
from core.security import decode_access_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

# Define el esquema de autenticación.
# tokenUrl apunta al endpoint donde el cliente obtiene el token.
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")


async def get_db() -> AsyncSession:
    """
    Dependencia para obtener una sesión de base de datos.
    Se asegura de que la sesión se cierre correctamente después de su uso.
    """
    async with async_session_maker() as session:
        yield session


async def get_current_user(
    token: str = Depends(reusable_oauth2), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependencia para obtener el usuario actual a partir de un token JWT.
    1. Decodifica el token.
    2. Obtiene el ID del usuario del payload.
    3. Busca al usuario en la base de datos.
    4. Devuelve el usuario si es válido; de lo contrario, lanza una excepción.
    """
    user_id = decode_access_token(token)
    user = await crud_user.get(db, id=uuid.UUID(user_id))
    if not user:
        # Si el token es válido pero el usuario no existe (p. ej. fue borrado),
        # se considera un fallo de autenticación.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: el usuario ya no existe.",
        )
    return user
