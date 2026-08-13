# /Users/carloslott/develop/python/pos-mvp/backend/app/models/sale.py
import uuid

from core.db import Base
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class Sale(Base):
    __tablename__ = "sales"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Foreign Keys
    store_id = Column(PG_UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pos_terminal_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("pos_terminals.id"), nullable=False
    )
    customer_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("customers.id"), nullable=True
    )  # A sale can be to an anonymous customer

    # Relationships
    store = relationship("Store", back_populates="sales")
    user = relationship("User", back_populates="sales")
    pos_terminal = relationship("PosTerminal", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")
    items = relationship(
        "SaleItem", back_populates="sale", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Sale(id={self.id}, total_amount={self.total_amount})>"


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Numeric(10, 2), nullable=False)

    # Foreign Keys
    sale_id = Column(PG_UUID(as_uuid=True), ForeignKey("sales.id"), nullable=False)
    product_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("products.id"), nullable=False
    )

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")

    def __repr__(self):
        return f"<SaleItem(product_id={self.product_id}, quantity={self.quantity})>"
