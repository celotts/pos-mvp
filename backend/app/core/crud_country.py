from core.crud_base import CRUDBase
from models.country import Country
from schemas.country import CountryCreate, CountryUpdate


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    def __init__(self, model: type[Country]):
        super().__init__(model)


crud_country = CRUDCountry(Country)
