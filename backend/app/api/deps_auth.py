from fastapi import Depends, HTTPException, status

from core.config import settings
from core.i18n import tr
from dependencies import get_current_user
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
        raise HTTPException(status_code=400, detail=tr("AUTH.USER_INACTIVE"))
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
            detail=tr("RBAC.NO_VALID_ROLE"),
        )

    # 2. Verificación de permisos (mejorada para ser robusta)
    # Se convierte el rol a mayúsculas y se eliminan espacios en blanco
    # para evitar problemas sutiles en los datos (ej. ' admin ', 'Admin').
    user_role_normalized = current_user.role.name.strip().upper()

    if user_role_normalized not in settings.PROTECTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=tr("RBAC.FORBIDDEN"),
        )
    return current_user


def require_permission(permission_code: str):
    """
    Fábrica de dependencias RBAC (Fase 3).

    Devuelve una dependencia que verifica que el usuario activo tenga el
    permiso solicitado (p. ej. `"sale:create"`). Los roles protegidos
    (SUPER_ADMIN/ADMIN) tienen acceso total. El rol del usuario y sus
    permisos llegan pre-cargados por `crud_user` (selectinload).
    """

    def permission_guard(
        current_user: User = get_current_active_user_dependency,
    ) -> User:
        role = current_user.role
        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=tr("RBAC.NO_VALID_ROLE"),
            )

        # Roles protegidos: acceso total (bypass de permisos granulares).
        if role.name.strip().upper() in settings.PROTECTED_ROLES:
            return current_user

        permitted_codes = {p.code for p in role.permissions}
        if permission_code not in permitted_codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=tr("RBAC.FORBIDDEN"),
            )
        return current_user

    return permission_guard
