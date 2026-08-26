from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from core.db import Base
from pgvector.sqlalchemy import VECTOR
from sqlalchemy import ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .sale import Sale


class SalesVector(Base):
    """
    Modelo para almacenar embeddings (vectores) de las ventas.
    Permite realizar búsquedas semánticas y de similitud utilizando pgvector.
    Está asociado directamente a un registro de venta (Sale) y almacena 
    tanto el contenido en texto como su representación vectorial.
    """
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

    sale: Mapped[Sale] = relationship(back_populates="sales_vectors")


# Define the specialized index for pgvector after the class definition.
# This index is crucial for efficient similarity searches and will be created
# by `Base.metadata.create_all`.
Index(
    "idx_sales_vectors_embedding",
    SalesVector.embedding,
    postgresql_using="ivfflat",
    postgresql_with={"lists": 100},
    postgresql_ops={"embedding": "vector_l2_ops"},
)
