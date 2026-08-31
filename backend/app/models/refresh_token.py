import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class RefreshToken(Base):
    """Token de refresco (C.3) con rotación y revocación.

    Guarda solo el hash del `jti` (nunca el token en claro) más el estado de
    revocación. Rotación: cada uso marca el anterior como revocado y emite
    uno nuevo, de modo que un token reutilizado queda invalidado.
    """

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    token_hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)

    def __repr__(self) -> str:
        return f"<RefreshToken(user_id={self.user_id}, revoked={self.revoked})>"
