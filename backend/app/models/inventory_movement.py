# backend/app/models/inventory_movement.py
"""Libro de movimientos de inventario.

Cada fila representa una entrada (+) o salida (-) de stock de un producto,
con un motivo (movement_type) y una referencia al documento origen. El stock
disponible de un producto se calcula como: SUM(entradas) - SUM(salidas).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from .product import Product
    from .store import Store
    from .user import User


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    # Tipos de movimiento (entrada o salida)
    # PURCHASE_IN          -> entrada por compra de producto
    # SALE_OUT             -> salida por venta
    # SALE_RETURN_IN       -> entrada por devolución de venta
    # PURCHASE_RETURN_OUT  -> salida por devolución de compra
    # EXPIRED_OUT          -> salida por producto vencido / merma
    # ADJUSTMENT           -> entrada o salida por ajuste manual
    DIRECTIONS = ("IN", "OUT")

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    store_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False, index=True
    )
    # Cantidad con signo: positivo = entrada, negativo = salida.
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    movement_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    # Documento origen (ej: sale_id, purchase_id). Para trazabilidad.
    reference_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    unit_cost: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True
    )

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id")
    )

    # Relaciones (ligeras, sin back_populates para evitar ciclos)
    product: Mapped[Product | None] = relationship("Product")
    store: Mapped[Store | None] = relationship("Store")
    creator: Mapped[User | None] = relationship("User")

    def __repr__(self) -> str:
        return (
            f"<InventoryMovement(product_id={self.product_id}, "
            f"qty={self.quantity}, type={self.movement_type})>"
        )
