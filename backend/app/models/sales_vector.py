from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.db import Base
from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .sale import Sale


class SalesVector(Base):
    __tablename__ = "sales_vectors"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sale_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sales.id", ondelete="CASCADE")
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(
        VECTOR(768)
    )  # Dimensión para nomic-embed-text

    sale: Mapped[Sale] = relationship()
