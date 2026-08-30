import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


# Propiedades base que comparten todos los esquemas de cliente
class CustomerBase(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None


# Propiedades requeridas al crear un cliente
class CustomerCreate(CustomerBase):
    full_name: str


# Propiedades que se pueden actualizar
class CustomerUpdate(CustomerBase):
    pass


# Propiedades almacenadas en la base de datos
class CustomerInDBBase(CustomerBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


# Esquema final que se devuelve al cliente en las respuestas de la API
class Customer(CustomerInDBBase):
    pass
