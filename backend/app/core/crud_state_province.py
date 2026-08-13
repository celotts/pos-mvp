from core.crud_base import CRUDBase
from models.state_province import StateProvince
from schemas.state_province import StateProvinceCreate, StateProvinceUpdate


class CRUDStateProvince(
    CRUDBase[StateProvince, StateProvinceCreate, StateProvinceUpdate]
):
    def __init__(self, model: type[StateProvince]):
        super().__init__(model)


crud_state_province = CRUDStateProvince(StateProvince)
