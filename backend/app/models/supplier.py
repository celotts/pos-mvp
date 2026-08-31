from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from .product import Product
    from .purchase import Purchase


class Supplier(Base):
    __tablename__ = "suppliers"

    __table_args__ = (
        Index(
            "uq_suppliers_tenant_email",
            "tenant_id",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    contact_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    address: Mapped[str | None] = mapped_column(String(255))

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )
    products: Mapped[list[Product]] = relationship(back_populates="supplier")
    purchases: Mapped[list[Purchase]] = relationship(back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(name='{self.name}')>"
