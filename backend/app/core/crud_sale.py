from core.crud_base import CRUDBase
from models.sale import Sale
from schemas.sale import SaleCreate, SaleUpdate
from sqlalchemy.orm import selectinload


class CRUDSale(CRUDBase[Sale, SaleCreate, SaleUpdate]):
    def __init__(self, model: type[Sale]):
        super().__init__(model)
        # Cargar la relación con el cliente por defecto
        self.default_loads = [selectinload(self.model.customer)]


crud_sale = CRUDSale(Sale)
