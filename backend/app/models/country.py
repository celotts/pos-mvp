import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .state_province import StateProvince


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    iso_code: Mapped[str] = mapped_column(
        String(3), unique=True, index=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationship to StateProvince
    states: Mapped[list["StateProvince"]] = relationship(  # This was already correct
        "StateProvince", back_populates="country"
    )

    def __repr__(self):
        return f"<Country(name='{self.name}')>"
