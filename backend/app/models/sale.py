# /Users/carloslott/develop/python/pos-mvp/backend/app/models/sale.py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

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
    from .accounts_receivable import AccountsReceivable
    from .customer import Customer
    from .pos_terminal import PosTerminal
    from .product import Product
    from .store import Store
    from .user import User


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Foreign Keys
    store_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    pos_terminal_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pos_terminals.id"), nullable=False
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id"), nullable=True
    )  # A sale can be to an anonymous customer

    # Relationships
    store: Mapped["Store"] = relationship("Store", back_populates="sales")
    user: Mapped["User"] = relationship("User", back_populates="sales")
    pos_terminal: Mapped["PosTerminal"] = relationship(
        "PosTerminal", back_populates="sales"
    )
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer", back_populates="sales"
    )
    items: Mapped[list["SaleItem"]] = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )
    accounts_receivable: Mapped[  # This line was already correct
        Optional["AccountsReceivable"]
    ] = (  # This line was already correct
        relationship(  # This line was already correct
            "AccountsReceivable", back_populates="sale", uselist=False
        )
    )

    def __repr__(self):
        return f"<Sale(id={self.id}, total_amount={self.total_amount})>"


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_sale: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Foreign Keys
    sale_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sales.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )

    # Relationships
    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="sale_items")

    def __repr__(self):
        return f"<SaleItem(product_id={self.product_id}, quantity={self.quantity})>"
