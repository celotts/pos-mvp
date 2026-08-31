from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.soft_delete import SoftDeleteMixin

if TYPE_CHECKING:
    from .sale import Sale


class Customer(Base, SoftDeleteMixin):
    __tablename__ = "customers"

    __table_args__ = (
        Index(
            "uq_customers_tenant_email",
            "tenant_id",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(255))

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )
    # Relationship to Sale
    sales: Mapped[list[Sale]] = relationship(  # This was already correct
        "Sale", back_populates="customer"
    )  # This was already correct

    def __repr__(self):
        return f"<Customer(full_name='{self.full_name}')>"
