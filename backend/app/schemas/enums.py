from enum import Enum


class ShiftStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class SaleStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"


class PurchaseStatus(str, Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class ARAPStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class CashAccountType(str, Enum):
    CASH = "CASH"
    BANK = "BANK"
