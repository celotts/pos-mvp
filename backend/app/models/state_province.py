import uuid

from core.db import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class StateProvince(Base):
    __tablename__ = "states"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)

    # Foreign Key
    country_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("countries.id"), nullable=False
    )

    # Relationships
    country = relationship("Country", back_populates="states")
    municipalities = relationship("Municipality", back_populates="state")

    def __repr__(self):
        return f"<StateProvince(name='{self.name}')>"
