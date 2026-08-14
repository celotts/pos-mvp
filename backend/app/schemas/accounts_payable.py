import uuid
from datetime import date, datetime

from pydantic import BaseModel

from .enums import ARAPStatus


class AccountsPayableBase(BaseModel):
    """Esquema base para una cuenta por pagar."""

    purchase_id: uuid.UUID
    supplier_id: uuid.UUID
    original_amount: float
    outstanding_amount: float
    due_date: date | None = None
    status: ARAPStatus = ARAPStatus.OPEN


class AccountsPayableCreate(AccountsPayableBase):
    """Esquema para crear una nueva cuenta por pagar."""


class AccountsPayableUpdate(BaseModel):
    """Esquema para actualizar una cuenta por pagar. Todos los campos son opcionales."""

    outstanding_amount: float | None = None
    due_date: date | None = None
    status: ARAPStatus | None = None


class AccountsPayable(AccountsPayableBase):
    """Esquema para devolver una cuenta por pagar en la API."""

    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
