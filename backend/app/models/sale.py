# /backend/app/models/sale.py
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from .accounts_receivable import AccountsReceivable
    from .customer import Customer
    from .pos_terminal import PosTerminal
    from .sale_item import SaleItem  # <-- AGREGADO
    from .sales_vector import SalesVector
    from .shift import Shift
    from .store import Store
    from .user import User


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sale_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_tax_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), server_default="0", nullable=False
    )
    status: Mapped[str] = mapped_column(
        SQLAlchemyEnum(
            "PENDING", "COMPLETED", "CANCELLED", name="sale_status", create_type=False
        ),
        nullable=False,
        server_default="PENDING",
    )
    payment_status: Mapped[str] = mapped_column(
        SQLAlchemyEnum(
            "UNPAID", "PAID", "PARTIALLY_PAID", name="payment_status", create_type=False
        ),
        nullable=False,
        server_default="UNPAID",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Foreign Keys
    store_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stores.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    pos_terminal_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("pos_terminals.id"), nullable=True
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("customers.id"), nullable=True
    )
    shift_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("shifts.id"), nullable=True
    )

    # Relationships
    store: Mapped["Store"] = relationship("Store", back_populates="sales")
    user: Mapped["User"] = relationship("User", back_populates="sales")
    pos_terminal: Mapped[Optional["PosTerminal"]] = relationship(
        "PosTerminal", back_populates="sales"
    )
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer", back_populates="sales"
    )
    shift: Mapped[Optional["Shift"]] = relationship("Shift", back_populates="sales")
    items: Mapped[list["SaleItem"]] = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )
    accounts_receivable: Mapped[Optional["AccountsReceivable"]] = relationship(
        "AccountsReceivable", back_populates="sale", uselist=False
    )
    sales_vectors: Mapped[list["SalesVector"]] = relationship(
        "SalesVector", back_populates="sale", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Sale(id={self.id}, total_amount={self.total_amount})>"


# SE ELIMINÓ LA CLASE SaleItem DE AQUÍ
