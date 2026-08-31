"""Contexto de tenancy por request (Fase 3).

`current_tenant_id` es un ContextVar que `get_current_user` establece con el
tenant del usuario autenticado. CRUDBase/CRUDService lo aplican automáticamente
en las queries, de modo que cada request solo ve/escribe datos de su compañía.
"""

import uuid
from contextvars import ContextVar

current_tenant_id: ContextVar[uuid.UUID | None] = ContextVar(
    "current_tenant_id", default=None
)


def set_current_tenant(tenant_id: uuid.UUID | None) -> None:
    """Establece el tenant activo para el request en curso."""
    current_tenant_id.set(tenant_id)


def get_current_tenant() -> uuid.UUID | None:
    """Devuelve el tenant activo del request (None fuera de peticiones HTTP)."""
    return current_tenant_id.get()