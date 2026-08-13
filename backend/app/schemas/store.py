from uuid import UUID

from pydantic import BaseModel


# Shared properties
class StoreBase(BaseModel):
    name: str
    address: str | None = None
    municipality_id: UUID | None = None


# Properties to receive on item creation
class StoreCreate(StoreBase):
    pass


# Properties to receive on item update
class StoreUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    municipality_id: UUID | None = None


# Properties shared by models in DB
class StoreInDBBase(StoreBase):
    id: UUID

    class Config:
        from_attributes = True


# Properties to return to client
class Store(StoreInDBBase):
    pass
