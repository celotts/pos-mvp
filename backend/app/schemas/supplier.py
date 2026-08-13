import uuid

from pydantic import BaseModel, EmailStr


# Shared properties
class SupplierBase(BaseModel):
    name: str
    contact_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None


# Properties to receive on item creation
class SupplierCreate(SupplierBase):
    name: str  # Make name required on creation


# Properties to receive on item update
class SupplierUpdate(SupplierBase):
    pass


# Properties shared by models in DB
class SupplierInDBBase(SupplierBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


# Properties to return to client
class Supplier(SupplierInDBBase):
    pass
