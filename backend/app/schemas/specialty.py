import uuid
from datetime import datetime

from pydantic import BaseModel


# Propiedades compartidas que tienen todos los esquemas
class SpecialtyBase(BaseModel):
    name: str | None = None
    description: str | None = None


# Propiedades para recibir en la creación desde la API
class SpecialtyCreate(SpecialtyBase):
    name: str


# Propiedades para recibir en la actualización desde la API
class SpecialtyUpdate(SpecialtyBase):
    pass


# Propiedades que están en la BD pero no necesariamente se exponen siempre
class SpecialtyInDBBase(SpecialtyBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Esquema final para devolver al cliente (respuesta de la API)
class Specialty(SpecialtyInDBBase):
    pass
