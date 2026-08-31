import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .enums import ARAPStatus


class AccountsPayableBase(BaseModel):
    """Esquema base para una cuenta por pagar."""

    purchase_id: uuid.UUID
    supplier_id: uuid.UUID
    original_amount: Decimal = Field(..., ge=0)
    outstanding_amount: Decimal = Field(..., ge=0)
    due_date: date | None = None
    status: ARAPStatus = ARAPStatus.OPEN


class AccountsPayableCreate(AccountsPayableBase):
    """Esquema para crear una nueva cuenta por pagar."""


class AccountsPayableUpdate(BaseModel):
    """Esquema para actualizar una cuenta por pagar. Todos los campos son opcionales."""

    outstanding_amount: Decimal | None = Field(None, ge=0)
    due_date: date | None = None
    status: ARAPStatus | None = None


class AccountsPayable(AccountsPayableBase):
    """Esquema para devolver una cuenta por pagar en la API."""

    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
