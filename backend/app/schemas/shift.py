import uuid
from datetime import datetime

from models.shift import ShiftStatus
from pydantic import BaseModel


# --- Shared Properties ---
class ShiftBase(BaseModel):
    pos_terminal_id: uuid.UUID
    store_id: uuid.UUID


# --- Properties for Creating a Shift ---
class ShiftOpen(ShiftBase):
    start_cash: float


# --- Properties for Closing a Shift ---
class ShiftClose(BaseModel):
    end_cash: float
    notes: str | None = None


# --- Properties to Return to Client ---
class Shift(ShiftBase):
    id: uuid.UUID
    user_id: uuid.UUID
    start_time: datetime
    end_time: datetime | None = None
    start_cash: float
    end_cash: float | None = None
    notes: str | None = None
    status: ShiftStatus

    class Config:
        from_attributes = True
