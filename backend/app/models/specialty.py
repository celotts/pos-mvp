import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from .user import User


class Specialty(Base):
    __tablename__ = "specialties"

    __table_args__ = (
        Index(
            "uq_specialties_tenant_name",
            "tenant_id",
            "name",
            unique=True,
            postgresql_where=text("name IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )

    # Relationships for audit
    created_by_user: Mapped[Optional["User"]] = (  # This was already correct
        relationship(  # This was already correct
            "User", foreign_keys=[created_by]
        )
    )
    updated_by_user: Mapped[Optional["User"]] = (  # This was already correct
        relationship(  # This was already correct
            "User", foreign_keys=[updated_by]
        )
    )

    def __repr__(self):
        return f"<Specialty(name='{self.name}')>"
