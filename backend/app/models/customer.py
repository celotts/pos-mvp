import uuid
from typing import TYPE_CHECKING

from core.db import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from .sale import Sale  # noqa: F401


class Customer(Base):
    __tablename__ = "customers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), unique=True, index=True, nullable=True)
    phone = Column(String(50))
    address = Column(String(255))

    # Relationship to Sale
    sales = relationship("Sale", back_populates="customer")

    def __repr__(self):
        return f"<Customer(full_name='{self.full_name}')>"
