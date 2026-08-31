import uuid

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(RoleBase):
    pass


class Role(RoleBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


class RoleWithPermissions(Role):
    """Rol con los códigos de permiso (para la UI de administración)."""

    permissions: list[str] = Field(
        default_factory=list, validation_alias="permission_codes"
    )
