# backend/app/models/purchase.py
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from .accounts_payable import AccountsPayable
    from .pos_terminal import PosTerminal
    from .product import Product
    from .role import Role
    from .supplier import Supplier
    from .user import User

from .store import Store  # Ensure Store is available at runtime


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    pos_terminal_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("pos_terminals.id"), nullable=True
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=False
    )
    # Specific purchase date, distinct from created_at audit field
    purchase_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")
    payment_status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="UNPAID",
    )
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )

    # Audit fields
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
    pos_terminal: Mapped[PosTerminal | None] = relationship(
        "PosTerminal", back_populates="purchases"
    )
    store: Mapped[Store] = relationship("Store", back_populates="purchases")
    supplier: Mapped[Supplier] = relationship("Supplier", back_populates="purchases")
    items: Mapped[list[PurchaseItem]] = relationship(
        "PurchaseItem", back_populates="purchase", cascade="all, delete-orphan"
    )
    accounts_payable: Mapped[AccountsPayable | None] = relationship(
        "AccountsPayable",
        back_populates="purchase",
        uselist=False,
    )
    creator: Mapped[User | None] = relationship(
        "User", foreign_keys=[created_by], back_populates="purchases"
    )
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
        return f"<Purchase(id={self.id}, total_amount={self.total_amount})>"


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quantity: Mapped[int] = mapped_column()
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Foreign Keys
    purchase_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("purchases.id"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )

    # Relationships
    purchase: Mapped[Purchase] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="purchase_items")

    def __repr__(self):
        return f"<PurchaseItem(product_id={self.product_id}, quantity={self.quantity})>"
