from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import (
    DATE,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .customer import Customer
    from .role import Role
    from .sale import Sale
    from .user import User


class AccountsReceivable(Base):
    __tablename__ = "accounts_receivable"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sale_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("sales.id"), unique=True, nullable=False
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False
    )
    original_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    outstanding_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    due_date: Mapped[date | None] = mapped_column(DATE)
    status: Mapped[str] = mapped_column(String, nullable=False, default="OPEN")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )

    created_by_role_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id")
    )
    updated_by_role_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id")
    )
    deleted_by_role_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id")
    )

    # Relationships
    sale: Mapped[Sale] = relationship("Sale", back_populates="accounts_receivable")
    customer: Mapped[Customer] = relationship("Customer")
    creator: Mapped[User | None] = relationship("User", foreign_keys=[created_by])
    updater: Mapped[User | None] = relationship("User", foreign_keys=[updated_by])
    deleter: Mapped[User | None] = relationship("User", foreign_keys=[deleted_by])
    creator_role: Mapped[Role | None] = relationship(
        "Role", foreign_keys=[created_by_role_id]
    )
    updater_role: Mapped[Role | None] = relationship(
        "Role", foreign_keys=[updated_by_role_id]
    )
    deleter_role: Mapped[Role | None] = relationship(
        "Role", foreign_keys=[deleted_by_role_id]
    )

    def __repr__(self):
        return f"<AccountsReceivable(id={self.id}, original_amount={self.original_amount})>"
