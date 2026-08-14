from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .sale import Sale  # noqa: F401


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(
        String(100), unique=True, index=True, nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(255))

    # Relationship to Sale
    sales: Mapped[list[Sale]] = relationship("Sale", back_populates="customer")

    def __repr__(self):
        return f"<Customer(full_name='{self.full_name}')>"
