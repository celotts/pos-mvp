import uuid

from core.db import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class Country(Base):
    __tablename__ = "countries"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    iso_code = Column(String(3), unique=True, index=True, nullable=False)

    # Relationship to StateProvince
    states = relationship("StateProvince", back_populates="country")

    def __repr__(self):
        return f"<Country(name='{self.name}')>"
