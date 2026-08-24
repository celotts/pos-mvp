from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import (
    ForeignKey,
    Numeric,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .sale import Sale

if TYPE_CHECKING:
    from .product import Product


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_sale: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    # Foreign Keys
    sale_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sales.id"), nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id"), nullable=False
    )

    # Relationships
    sale: Mapped[Sale] = relationship("Sale", back_populates="items")
    product: Mapped[Product] = relationship("Product", back_populates="sale_items")

    def __repr__(self):
        return f"<SaleItem(product_id={self.product_id}, quantity={self.quantity})>"
