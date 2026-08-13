from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .cash_account import CashAccount
    from .pos_terminal import PosTerminal
    from .store import Store
    from .user import User


class ShiftStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class Shift(Base):
    __tablename__ = "shifts"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    start_cash: Mapped[float] = mapped_column()
    end_cash: Mapped[float | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column()
    status: Mapped[ShiftStatus] = mapped_column(
        Enum(ShiftStatus), default=ShiftStatus.OPEN, nullable=False
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    pos_terminal_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("pos_terminals.id"), nullable=False
    )
    store_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)

    # Relationships
    user: Mapped[User] = relationship(back_populates="shifts")
    pos_terminal: Mapped[PosTerminal] = relationship(back_populates="shifts")
    store: Mapped[Store] = relationship(back_populates="shifts")
    cash_transactions: Mapped[list[CashAccount]] = relationship(back_populates="shift")

    def __repr__(self):
        return (
            f"<Shift(id={self.id}, user_id={self.user_id}, "
            f"start_time={self.start_time})>"
        )
