# backend/app/models/purchase.py
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .pos_terminal import PosTerminal
    from .product import Product
    from .store import Store
    from .user import User


class Purchase(Base):
    __tablename__ = "purchases"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Foreign Keys
    store_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # A purchase might be anonymous
    pos_terminal_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("pos_terminals.id"), nullable=False
    )

    # Relationships
    store: Mapped[Store] = relationship(back_populates="purchases")
    user: Mapped[User | None] = relationship(back_populates="purchases")
    pos_terminal: Mapped[PosTerminal] = relationship(back_populates="purchases")
    items: Mapped[list[PurchaseItem]] = relationship(
        "PurchaseItem", back_populates="purchase", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Purchase(id={self.id}, total_amount={self.total_amount})>"


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quantity: Mapped[int] = mapped_column()
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Foreign Keys
    purchase_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("purchases.id"))
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"))

    # Relationships
    purchase: Mapped[Purchase] = relationship(back_populates="items")
    product: Mapped[Product] = relationship(back_populates="purchase_items")

    def __repr__(self):
        return f"<PurchaseItem(product_id={self.product_id}, quantity={self.quantity})>"
