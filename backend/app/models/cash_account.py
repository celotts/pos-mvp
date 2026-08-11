import enum
import uuid

from core.db import Base
from sqlalchemy import UUID, Column, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func


class CashAccountType(str, enum.Enum):
    CASH = "CASH"
    BANK = "BANK"


class CashAccount(Base):
    __tablename__ = "cash_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    account_type = Column(Enum(CashAccountType), nullable=False)
    current_balance = Column(Numeric(18, 2), nullable=False, default=0)
    currency = Column(String(3), nullable=False, default="MXN")

    created_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.now())
    deleted_at = Column(TIMESTAMP(timezone=True))

    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    created_by_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    updated_by_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
    deleted_by_role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))
