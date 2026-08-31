import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from .municipality import Municipality
    from .purchase import Purchase
    from .sale import Sale
    from .shift import Shift


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    address: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Foreign Key
    municipality_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("municipalities.id"), nullable=True
    )

    # Relationships
    municipality: Mapped[Optional["Municipality"]] = (  # This was already correct
        relationship(  # This was already correct
            "Municipality", back_populates="stores"
        )
    )

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )

    # Relationships to transactions
    purchases: Mapped[list["Purchase"]] = relationship(  # This was already correct
        "Purchase", back_populates="store"
    )
    sales: Mapped[list["Sale"]] = relationship(  # This was already correct
        "Sale", back_populates="store"
    )  # This was already correct
    shifts: Mapped[list["Shift"]] = relationship(  # This was already correct
        "Shift", back_populates="store"
    )  # This was already correct

    def __repr__(self):
        return f"<Store(name='{self.name}')>"
