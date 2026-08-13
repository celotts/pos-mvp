from core.crud_base import CRUDBase
from models.store import Store
from schemas.store import StoreCreate, StoreUpdate
from sqlalchemy.orm import selectinload


class CRUDStore(CRUDBase[Store, StoreCreate, StoreUpdate]):
    def __init__(self, model: type[Store]):
        super().__init__(model)
        self.default_loads = [selectinload(self.model.municipality)]


crud_store = CRUDStore(Store)
