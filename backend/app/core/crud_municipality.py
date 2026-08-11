from core.crud_base import CRUDBase
from models.municipality import Municipality
from schemas.municipality import MunicipalityCreate, MunicipalityUpdate
from sqlalchemy.orm import selectinload


class CRUDMunicipality(CRUDBase[Municipality, MunicipalityCreate, MunicipalityUpdate]):
    def __init__(self, model: type[Municipality]):
        super().__init__(model)
        self.default_loads = [selectinload(self.model.state)]


crud_municipality = CRUDMunicipality(Municipality)
