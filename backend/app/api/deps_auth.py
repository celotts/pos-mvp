from core.config import settings
from dependencies import get_current_user
from fastapi import Depends, HTTPException, status
from models.user import User

# Definir las dependencias a nivel de módulo para evitar RuffB008
get_current_user_dependency = Depends(get_current_user)


def get_current_active_user(
    current_user: User = get_current_user_dependency,
) -> User:
    """
    Dependencia que obtiene el usuario actual y verifica si está activo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive.")
    return current_user


# Ahora que la función está definida, podemos crear la dependencia que la usa.
get_current_active_user_dependency = Depends(get_current_active_user)


def get_current_admin_user(
    current_user: User = get_current_active_user_dependency,
) -> User:
    """
    Dependencia que obtiene el usuario activo y verifica si es un SUPER_ADMIN.
    """
    # 1. Verificación de robustez: ¿El rol del usuario existe?
    if not current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have a valid role assigned or the role has been deleted.",
        )

    # 2. Verificación de permisos (mejorada para ser robusta)
    # Se convierte el rol a mayúsculas y se eliminan espacios en blanco
    # para evitar problemas sutiles en los datos (ej. ' admin ', 'Admin').
    user_role_normalized = current_user.role.name.strip().upper()

    if user_role_normalized not in settings.PROTECTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have the necessary privileges.",
        )
    return current_user
