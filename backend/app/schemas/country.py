import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# Propiedades base que comparten todos los esquemas
class CountryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    iso_code: str = Field(..., min_length=2, max_length=3)


# Propiedades para la creación
class CountryCreate(CountryBase):
    pass


# Propiedades para la actualización
class CountryUpdate(CountryBase):
    pass


# Propiedades almacenadas en la BD, para la respuesta de la API
class Country(CountryBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
