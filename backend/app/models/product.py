from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .purchase import PurchaseItem
    from .sale import SaleItem
    from .supplier import Supplier


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    sku: Mapped[str | None] = mapped_column(String(100), unique=True, index=True)

    # Foreign Key to Supplier
    supplier_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("suppliers.id"), nullable=True
    )

    # Relationships
    supplier: Mapped[Supplier | None] = relationship(  # This was already correct
        back_populates="products"
    )  # This was already correct
    purchase_items: Mapped[list[PurchaseItem]] = (
        relationship(  # This was already correct
            back_populates="product"
        )
    )  # This was already correct
    sale_items: Mapped[list[SaleItem]] = relationship(  # This was already correct
        back_populates="product"
    )  # This was already correct

    def __repr__(self):
        return f"<Product(name='{self.name}', sku='{self.sku}')>"
