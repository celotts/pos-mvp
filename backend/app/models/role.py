import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base
from core.soft_delete import SoftDeleteMixin

from .permission import role_permissions

if TYPE_CHECKING:
    from .permission import Permission
    from .pos_terminal import PosTerminal
    from .user import User


class Role(Base, SoftDeleteMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="role")

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )

    @property
    def permission_codes(self) -> list[str]:
        return sorted({p.code for p in self.permissions})

    # Relationships to PosTerminal for audit trails
    role_created_pos_terminals: Mapped[list["PosTerminal"]] = relationship(
        "PosTerminal",
        back_populates="created_by_role_rel",
        foreign_keys="PosTerminal.created_by_role_id",
    )
    role_updated_pos_terminals: Mapped[list["PosTerminal"]] = relationship(
        "PosTerminal",
        back_populates="updated_by_role_rel",
        foreign_keys="PosTerminal.updated_by_role_id",
    )
    role_deleted_pos_terminals: Mapped[list["PosTerminal"]] = relationship(
        "PosTerminal",
        back_populates="deleted_by_role_rel",
        foreign_keys="PosTerminal.deleted_by_role_id",
    )
