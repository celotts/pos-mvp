import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from .country import Country
    from .municipality import Municipality


class StateProvince(Base):
    __tablename__ = "states"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Foreign Key
    country_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False
    )

    # Relationships
    country: Mapped["Country"] = relationship(
        "Country", back_populates="states"
    )  # This was already correct
    municipalities: Mapped[list["Municipality"]] = (
        relationship(  # This was already correct
            "Municipality", back_populates="state"
        )
    )

    def __repr__(self):
        return f"<StateProvince(name='{self.name}')>"
