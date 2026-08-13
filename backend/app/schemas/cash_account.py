import uuid
from datetime import datetime
from decimal import Decimal

from models.cash_account import CashAccountType
from pydantic import BaseModel, Field


class CashAccountBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    account_type: CashAccountType
    current_balance: Decimal = Field(Decimal("0.00"), ge=0, decimal_places=2)
    currency: str = Field("MXN", min_length=3, max_length=3)


class CashAccountCreate(CashAccountBase):
    pass


class CashAccountUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    account_type: CashAccountType | None = None
    # El balance no se debería poder actualizar directamente, sino a través de transacciones.
    # currency: str | None = Field(None, min_length=3, max_length=3)


class CashAccount(CashAccountBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
