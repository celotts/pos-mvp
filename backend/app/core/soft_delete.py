"""Mixin de soft-delete para entidades (C.4).

Agrega `is_deleted`, `deleted_at` y `deleted_by` a un modelo sin tocar su
esquema existente. El CRUD base lo usa para hacer borrado lógico y filtrar
las filas borradas por defecto.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Uuid
from sqlalchemy.orm import Mapped, mapped_column


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
