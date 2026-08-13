from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .pos_terminal import PosTerminal
    from .user import User


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    # Relación inversa con User
    users: Mapped[list[User]] = relationship("User", back_populates="role")

    # Relaciones inversas con PosTerminal para auditoría
    role_created_pos_terminals: Mapped[list[PosTerminal]] = relationship(
        "PosTerminal",
        back_populates="created_by_role_rel",
        foreign_keys="PosTerminal.created_by_role_id",
    )
    role_updated_pos_terminals: Mapped[list[PosTerminal]] = relationship(
        "PosTerminal",
        back_populates="updated_by_role_rel",
        foreign_keys="PosTerminal.updated_by_role_id",
    )
    role_deleted_pos_terminals: Mapped[list[PosTerminal]] = relationship(
        "PosTerminal",
        back_populates="deleted_by_role_rel",
        foreign_keys="PosTerminal.deleted_by_role_id",
    )
