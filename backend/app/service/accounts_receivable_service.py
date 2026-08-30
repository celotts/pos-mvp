from models.accounts_receivable import AccountsReceivable
from schemas.accounts_receivable import (
    AccountsReceivableCreate,
    AccountsReceivableUpdate,
)

from .base_service import CRUDService


class AccountsReceivableService(
    CRUDService[AccountsReceivable, AccountsReceivableCreate, AccountsReceivableUpdate]
):
    """
    Servicio para las operaciones CRUD de Cuentas por Cobrar.
    """


accounts_receivable_service = AccountsReceivableService(AccountsReceivable)
