from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship  # type: ignore

from core.db import Base
from core.soft_delete import SoftDeleteMixin

# Esto solo lo lee el IDE para el autocompletado y los tipos,
# evitando importaciones circulares en ejecución.
if TYPE_CHECKING:
    from .pos_terminal import PosTerminal
    from .purchase import Purchase
    from .role import Role
    from .sale import Sale
    from .shift import Shift

from .purchase import Purchase  # Needed at runtime for foreign_keys


class User(Base, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )

    role: Mapped[Role] = relationship(  # This was already correct
        "Role", back_populates="users", foreign_keys=[role_id]
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )

    # Control de intentos de login (bloqueo de cuenta)
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def is_locked(self) -> bool:
        if not self.locked_until:
            return False
        return self.locked_until > datetime.now(timezone.utc)

    # Relaciones inversas con transacciones
    purchases: Mapped[list[Purchase]] = relationship(  # This was already correct
        "Purchase", foreign_keys=[Purchase.created_by], back_populates="creator"
    )
    sales: Mapped[list[Sale]] = relationship(  # This was already correct
        back_populates="user"
    )  # This was already correct
    shifts: Mapped[list[Shift]] = relationship(  # This was already correct
        back_populates="user"
    )  # This was already correct

    # Relaciones inversas con PosTerminal para auditoría
    created_pos_terminals: Mapped[list[PosTerminal]] = (  # This was already correct
        relationship(  # This was already correct
            back_populates="created_by_rel", foreign_keys="PosTerminal.created_by"
        )
    )
    updated_pos_terminals: Mapped[list[PosTerminal]] = (  # This was already correct
        relationship(  # This was already correct
            back_populates="updated_by_rel", foreign_keys="PosTerminal.updated_by"
        )
    )
    deleted_pos_terminals: Mapped[list[PosTerminal]] = (  # This was already correct
        relationship(  # This was already correct
            back_populates="deleted_by_rel", foreign_keys="PosTerminal.deleted_by"
        )
    )
