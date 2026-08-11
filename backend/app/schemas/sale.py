import uuid
from datetime import datetime
from decimal import Decimal

from models.sale import PaymentStatus, SaleStatus
from pydantic import BaseModel, Field

from .customer import Customer  # Importa el schema de Customer


class SaleBase(BaseModel):
    customer_id: uuid.UUID | None = None
    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    total_tax_amount: Decimal = Field(..., ge=0, decimal_places=2)
    discount_amount: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2)
    status: SaleStatus = SaleStatus.COMPLETED
    payment_status: PaymentStatus = PaymentStatus.PAID


class SaleCreate(SaleBase):
    # El ID de la terminal se usará para encontrar el turno activo
    pos_terminal_id: uuid.UUID


class SaleUpdate(BaseModel):
    # Por ahora, solo permitimos cancelar una venta
    status: SaleStatus


class Sale(SaleBase):
    id: uuid.UUID
    sale_date: datetime
    shift_id: uuid.UUID
    pos_terminal_id: uuid.UUID
    customer: "Customer" | None = None

    class Config:
        from_attributes = True


# Reconstruye el modelo para resolver la referencia de tipo "Customer"
Sale.model_rebuild()
