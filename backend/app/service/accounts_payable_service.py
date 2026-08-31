from models.accounts_payable import AccountsPayable
from schemas.accounts_payable import AccountsPayableCreate, AccountsPayableUpdate

from .base_service import CRUDService


class AccountsPayableService(
    CRUDService[AccountsPayable, AccountsPayableCreate, AccountsPayableUpdate]
):
    """
    Servicio para las operaciones CRUD de Cuentas por Pagar.
    """


accounts_payable_service = AccountsPayableService(AccountsPayable)
