from uuid import UUID

from pydantic import BaseModel


# Shared properties
class PosTerminalBase(BaseModel):
    name: str
    location: str | None = None
    is_active: bool = True


# Properties to receive on item creation
class PosTerminalCreate(PosTerminalBase):
    pass


# Properties to receive on item update
class PosTerminalUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    is_active: bool | None = None


# Properties shared by models in DB
class PosTerminalInDBBase(PosTerminalBase):
    id: UUID

    class Config:
        from_attributes = True


# Properties to return to client
class PosTerminal(PosTerminalInDBBase):
    pass
