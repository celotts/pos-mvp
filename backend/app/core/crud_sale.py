from core.crud_base import CRUDBase
from models.sale import Sale
from schemas.sale import SaleCreate  # Usamos SaleCreate, no hay Update para Sale


class CRUDSale(CRUDBase[Sale, SaleCreate, SaleCreate]):
    def __init__(self, model: type[Sale]):
        super().__init__(model)


crud_sale = CRUDSale(Sale)
