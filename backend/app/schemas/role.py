import uuid

from pydantic import BaseModel


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
