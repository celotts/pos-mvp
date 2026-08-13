from core.crud_base import CRUDBase
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def __init__(self, model: type[Customer]):
        super().__init__(model)


crud_customer = CRUDCustomer(Customer)
