import uuid

from core.db import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    state_id = Column(PG_UUID(as_uuid=True), ForeignKey("states.id"), nullable=False)

    state = relationship("StateProvince", back_populates="municipalities")

    # Relación inversa con Store
    stores = relationship("Store", back_populates="municipality")
