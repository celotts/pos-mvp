from uuid import UUID

from pydantic import BaseModel


# --- SaleItem Schemas ---
class SaleItemBase(BaseModel):
    product_id: UUID
    quantity: int


class SaleItemCreate(SaleItemBase):
    pass


class SaleItem(SaleItemBase):
    id: UUID
    price_at_sale: float

    class Config:
        from_attributes = True


# --- Sale Schemas ---
class SaleBase(BaseModel):
    store_id: UUID
    pos_terminal_id: UUID
    customer_id: UUID | None = None


class SaleCreate(SaleBase):
    items: list[SaleItemCreate]


class Sale(SaleBase):
    id: UUID
    user_id: UUID
    total_amount: float
    items: list[SaleItem] = []

    class Config:
        from_attributes = True
