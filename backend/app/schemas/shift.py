import uuid
from datetime import datetime
from decimal import Decimal

from models.shift import ShiftStatus
from pydantic import BaseModel


# --- Shared Properties ---
class ShiftBase(BaseModel):
    pos_terminal_id: uuid.UUID
    store_id: uuid.UUID


# --- Properties for Creating a Shift ---
class ShiftOpen(ShiftBase):
    starting_cash: Decimal


# --- Properties for Closing a Shift ---
class ShiftClose(BaseModel):
    ending_cash: Decimal
    notes: str | None = None


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
