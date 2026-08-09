from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import Boolean, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Esto solo lo lee el IDE para el autocompletado y los tipos,
# evitando importaciones circulares en ejecución.
if TYPE_CHECKING:
    from app.models.role import (
        Role,
    )  # Ajusta la ruta según dónde tengas tu archivo role.py


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), default="N/A")
    phone: Mapped[str | None] = mapped_column(String(255), default="0000000000")
    phone2: Mapped[str | None] = mapped_column(String(255), default="0000000000")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )

    role: Mapped[Role] = relationship(
        "Role", back_populates="users", foreign_keys=[role_id]
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(), server_default=func.now(), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)
