import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from .enums import ARAPStatus


class AccountsReceivableBase(BaseModel):
    """Esquema base para una cuenta por cobrar."""

    sale_id: uuid.UUID
    customer_id: uuid.UUID
    original_amount: Decimal
    outstanding_amount: Decimal
    due_date: date | None = None
    status: ARAPStatus = ARAPStatus.OPEN


class AccountsReceivableCreate(AccountsReceivableBase):
    """Esquema para crear una nueva cuenta por cobrar."""


class AccountsReceivableUpdate(BaseModel):
    """Esquema para actualizar una cuenta por cobrar. Todos los campos son opcionales."""

    outstanding_amount: Decimal | None = None
    due_date: date | None = None
    status: ARAPStatus | None = None


class AccountsReceivable(AccountsReceivableBase):
    """Esquema para devolver una cuenta por cobrar en la API."""

    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
