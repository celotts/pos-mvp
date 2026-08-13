from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


# Shared properties
class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    sku: str
    supplier_id: UUID | None = None


# Properties to receive on item creation
class ProductCreate(ProductBase):
    pass


# Properties to receive on item update
class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = None
    sku: str | None = None
    supplier_id: UUID | None = None


# Properties to return to client
class Product(ProductBase):
    id: UUID

    class Config:
        from_attributes = True
