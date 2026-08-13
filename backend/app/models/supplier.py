import uuid

from core.db import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    contact_name = Column(String(100))
    phone = Column(String(50))
    email = Column(String(100), unique=True, index=True, nullable=True)
    address = Column(String(255))

    products = relationship("Product", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(name='{self.name}')>"
