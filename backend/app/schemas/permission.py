import uuid

from pydantic import BaseModel


class PermissionBase(BaseModel):
    code: str
    description: str | None = None
    module: str


class Permission(PermissionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class RolePermissionsUpdate(BaseModel):
    """Lista de códigos de permiso a asignar a un rol (reemplaza por completo)."""

    permission_codes: list[str]
