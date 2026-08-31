import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from models.shift import ShiftStatus


# --- Shared Properties ---
class ShiftBase(BaseModel):
    pos_terminal_id: uuid.UUID
    store_id: uuid.UUID


# --- Properties for Creating a Shift ---
class ShiftOpen(ShiftBase):
    starting_cash: Decimal = Field(..., ge=0)


# --- Properties for Closing a Shift ---
class ShiftClose(BaseModel):
    ending_cash: Decimal = Field(..., ge=0)
    notes: str | None = Field(None, max_length=500)


# --- Properties to Return to Client ---
class Shift(ShiftBase):
    id: uuid.UUID
    user_id: uuid.UUID
    start_time: datetime
    end_time: datetime | None = None
    starting_cash: Decimal
    ending_cash: Decimal | None = None
    notes: str | None = None
    status: ShiftStatus

    class Config:
        from_attributes = True
