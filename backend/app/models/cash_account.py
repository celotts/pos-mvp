import enum
import uuid

from core.db import Base
from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship


class CashAccountType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class CashAccount(Base):
    __tablename__ = "cash_accounts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Numeric(10, 2), nullable=False)
    type = Column(Enum(CashAccountType), nullable=False)
    description = Column(String(255))
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    shift_id = Column(PG_UUID(as_uuid=True), ForeignKey("shifts.id"), nullable=False)
    shift = relationship("Shift", back_populates="cash_transactions")

    def __repr__(self):
        return f"<CashAccount(id={self.id}, type='{self.type.value}', amount={self.amount})>"
