import uuid

from pydantic import BaseModel


# Shared properties
class StateProvinceBase(BaseModel):
    name: str
    country_id: uuid.UUID


# Properties to receive on item creation
class StateProvinceCreate(StateProvinceBase):
    pass


# Properties to receive on item update
class StateProvinceUpdate(BaseModel):
    name: str | None = None
    country_id: uuid.UUID | None = None


# Properties shared by models in DB
class StateProvinceInDBBase(StateProvinceBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


# Properties to return to client
class StateProvince(StateProvinceInDBBase):
    pass
