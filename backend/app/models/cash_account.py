from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base
from core.soft_delete import SoftDeleteMixin


class CashAccountType(enum.Enum):
    CASH = "CASH"
    BANK = "BANK"


class CashAccount(Base, SoftDeleteMixin):
    __tablename__ = "cash_accounts"

    __table_args__ = (
        Index(
            "uq_cash_accounts_tenant_name",
            "tenant_id",
            "name",
            unique=True,
            postgresql_where=text("name IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[CashAccountType] = mapped_column(
        Enum(CashAccountType), nullable=False
    )
    current_balance: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, default=Decimal("0.0")
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="MXN")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )

    def __repr__(self):
        return f"<CashAccount(name='{self.name}', balance={self.current_balance})>"
