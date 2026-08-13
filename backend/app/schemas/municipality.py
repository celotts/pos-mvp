from uuid import UUID

from pydantic import BaseModel


# Shared properties
class MunicipalityBase(BaseModel):
    name: str
    state_id: UUID


# Properties to receive on item creation
class MunicipalityCreate(MunicipalityBase):
    pass


# Properties to receive on item update
class MunicipalityUpdate(BaseModel):
    name: str | None = None
    state_id: UUID | None = None


# Properties shared by models in DB
class MunicipalityInDBBase(MunicipalityBase):
    id: UUID

    class Config:
        from_attributes = True


# Properties to return to client
class Municipality(MunicipalityInDBBase):
    pass
