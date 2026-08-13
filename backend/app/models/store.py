import uuid

from core.db import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class Store(Base):
    __tablename__ = "stores"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    address = Column(String(255))

    # Foreign Key
    municipality_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("municipalities.id"), nullable=True
    )

    # Relationships
    municipality = relationship("Municipality", back_populates="stores")

    # Relationships to transactions
    purchases = relationship("Purchase", back_populates="store")
    sales = relationship("Sale", back_populates="store")
    shifts = relationship("Shift", back_populates="store")

    def __repr__(self):
        return f"<Store(name='{self.name}')>"
