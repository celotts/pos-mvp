from core.crud_base import CRUDBase
from models.product import Product
from schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def __init__(self, model: type[Product]):
        super().__init__(model)


crud_product = CRUDProduct(Product)
