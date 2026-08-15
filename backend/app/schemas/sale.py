import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class SaleStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"


# --- SaleItem Schemas ---
class SaleItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    id: uuid.UUID
    price_at_sale: Decimal

    class Config:
        from_attributes = True


# --- Sale Schemas ---
class SaleBase(BaseModel):
    store_id: uuid.UUID
    pos_terminal_id: uuid.UUID
    customer_id: uuid.UUID | None = None


class SaleCreate(SaleBase):
    items: list[SaleItemCreate]


class SaleUpdate(BaseModel):
    """Esquema para actualizar una venta. Típicamente para cambiar su estado."""

    customer_id: uuid.UUID | None = None
    status: SaleStatus | None = None
    payment_status: PaymentStatus | None = None


class Sale(BaseModel):
    id: uuid.UUID
    total_amount: Decimal
    user_id: uuid.UUID
    created_at: datetime
    items: list[SaleItem] = []

    class Config:
        from_attributes = True
