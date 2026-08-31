from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.soft_delete import SoftDeleteMixin

if TYPE_CHECKING:
    from .purchase import Purchase
    from .role import Role
    from .sale import Sale
    from .shift import Shift
    from .user import User


class PosTerminal(Base, SoftDeleteMixin):
    __tablename__ = "pos_terminals"

    __table_args__ = (
        Index(
            "uq_pos_terminals_tenant_name",
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
    location: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

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

    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    created_by_role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id"), nullable=True
    )
    updated_by_role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id"), nullable=True
    )
    deleted_by_role_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("roles.id"), nullable=True
    )

    # Relationships with Users
    created_by_rel: Mapped[User | None] = relationship(  # This was already correct
        "User", foreign_keys=[created_by], back_populates="created_pos_terminals"
    )
    updated_by_rel: Mapped[User | None] = relationship(  # This was already correct
        "User", foreign_keys=[updated_by], back_populates="updated_pos_terminals"
    )
    deleted_by_rel: Mapped[User | None] = relationship(  # This was already correct
        "User", foreign_keys=[deleted_by], back_populates="deleted_pos_terminals"
    )

    # Relationships with Roles
    created_by_role_rel: Mapped[Role | None] = relationship(  # This was already correct
        "Role",
        foreign_keys=[created_by_role_id],
        back_populates="role_created_pos_terminals",
    )
    updated_by_role_rel: Mapped[Role | None] = relationship(  # This was already correct
        "Role",
        foreign_keys=[updated_by_role_id],
        back_populates="role_updated_pos_terminals",
    )
    deleted_by_role_rel: Mapped[Role | None] = relationship(  # This was already correct
        "Role",
        foreign_keys=[deleted_by_role_id],
        back_populates="role_deleted_pos_terminals",
    )

    # Relationship with Purchases
    purchases: Mapped[list[Purchase]] = relationship(  # This was already correct
        "Purchase", back_populates="pos_terminal"
    )

    # Relationship with Sales
    sales: Mapped[list[Sale]] = relationship(  # This was already correct
        "Sale", back_populates="pos_terminal"
    )  # This was already correct

    # Relationship with Shifts
    shifts: Mapped[list[Shift]] = relationship(  # This was already correct
        "Shift", back_populates="pos_terminal"
    )  # This was already correct
