from core.crud_base import CRUDBase
from models.cash_account import CashAccount
from schemas.cash_account import CashAccountCreate, CashAccountUpdate


class CRUDCashAccount(CRUDBase[CashAccount, CashAccountCreate, CashAccountUpdate]):
    pass


crud_cash_account = CRUDCashAccount(CashAccount)
