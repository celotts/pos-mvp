import uuid

from core.db import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class PosTerminal(Base):
    __tablename__ = "pos_terminals"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    location = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    deleted_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"))

    created_by_role_id = Column(PG_UUID(as_uuid=True), ForeignKey("roles.id"))
    updated_by_role_id = Column(PG_UUID(as_uuid=True), ForeignKey("roles.id"))
    deleted_by_role_id = Column(PG_UUID(as_uuid=True), ForeignKey("roles.id"))

    # Relaciones con Users
    created_by_rel = relationship(
        "User", foreign_keys=[created_by], backref="created_pos_terminals"
    )
    updated_by_rel = relationship(
        "User", foreign_keys=[updated_by], backref="updated_pos_terminals"
    )
    deleted_by_rel = relationship(
        "User", foreign_keys=[deleted_by], backref="deleted_pos_terminals"
    )

    # Relaciones con Roles (¡Añadidas para completar la auditoría!)
    created_by_role_rel = relationship(
        "Role", foreign_keys=[created_by_role_id], backref="created_pos_terminals"
    )
    updated_by_role_rel = relationship(
        "Role", foreign_keys=[updated_by_role_id], backref="updated_pos_terminals"
    )
    deleted_by_role_rel = relationship(
        "Role", foreign_keys=[deleted_by_role_id], backref="deleted_pos_terminals"
    )
