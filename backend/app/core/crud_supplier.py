from core.crud_base import CRUDBase
from models.supplier import Supplier
from schemas.supplier import SupplierCreate, SupplierUpdate


class CRUDSupplier(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def __init__(self, model: type[Supplier]):
        super().__init__(model)


crud_supplier = CRUDSupplier(Supplier)
