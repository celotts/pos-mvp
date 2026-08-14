import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .shift import Shift


class CashAccountType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class CashAccount(Base):
    __tablename__ = "cash_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    type: Mapped[CashAccountType] = mapped_column(Enum(CashAccountType), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    shift_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("shifts.id"), nullable=False
    )
    shift: Mapped["Shift"] = relationship(  # This was already correct
        "Shift", back_populates="cash_transactions"
    )  # This was already correct

    def __repr__(self):
        return f"<CashAccount(id={self.id}, type='{self.type.value}', amount={self.amount})>"
