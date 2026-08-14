import uuid
from datetime import datetime

from pydantic import BaseModel

from .enums import PaymentStatus, PurchaseStatus


# --- PurchaseItem Schemas ---
class PurchaseItemBase(BaseModel):
    product_id: uuid.UUID
    quantity: int


class PurchaseItemCreate(PurchaseItemBase):
    price_at_purchase: float  # El precio al que compramos el producto


class PurchaseItem(PurchaseItemBase):
    id: uuid.UUID
    price_at_purchase: float

    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    """Esquema base para una compra."""

    supplier_id: uuid.UUID
    total_amount: float
    total_tax_amount: float
    status: PurchaseStatus = PurchaseStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.UNPAID


class PurchaseCreate(BaseModel):
    """Esquema para crear una nueva compra. Los totales se calculan en el backend."""

    supplier_id: uuid.UUID
    items: list[PurchaseItemCreate]


class PurchaseUpdate(BaseModel):
    """Esquema para actualizar una compra. Todos los campos son opcionales."""

    supplier_id: uuid.UUID | None = None
    status: PurchaseStatus | None = None
    payment_status: PaymentStatus | None = None


class Purchase(PurchaseBase):
    """Esquema para devolver una compra en la API."""

    id: uuid.UUID
    purchase_date: datetime
    items: list[PurchaseItem] = []

    class Config:
        from_attributes = True
