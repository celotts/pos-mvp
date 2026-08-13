from core.crud_base import CRUDBase
from models.municipality import Municipality
from schemas.municipality import MunicipalityCreate, MunicipalityUpdate


class CRUDMunicipality(CRUDBase[Municipality, MunicipalityCreate, MunicipalityUpdate]):
    def __init__(self, model: type[Municipality]):
        super().__init__(model)


crud_municipality = CRUDMunicipality(Municipality)
