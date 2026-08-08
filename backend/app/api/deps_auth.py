from dependencies import get_current_user
from fastapi import Depends, HTTPException, status
from models.user import User


def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependencia que verifica si el usuario actual es un administrador.
    Lanza una excepción HTTP 403 si el usuario no tiene el rol 'ADMIN'.
    """
    if not current_user.role or current_user.role.name != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no tiene suficientes privilegios.",
        )
    return current_user
