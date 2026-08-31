from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# Shared properties
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: Decimal = Field(..., ge=0)
    sku: str = Field(..., min_length=1, max_length=100)
    supplier_id: UUID | None = None


# Properties to receive on item creation
class ProductCreate(ProductBase):
    pass


# Properties to receive on item update
class ProductUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: Decimal | None = Field(None, ge=0)
    sku: str | None = Field(None, min_length=1, max_length=100)
    supplier_id: UUID | None = None


# Properties to return to client
class Product(ProductBase):
    id: UUID

    class Config:
        from_attributes = True
