from core.crud_base import CRUDBase
from models.supplier import Supplier
from schemas.supplier import SupplierCreate, SupplierUpdate


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    pass


crud_supplier = CRUDSupplier(Supplier)
