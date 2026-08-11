import uuid

from core import crud_specialty
from fastapi import HTTPException, status
from models.specialty import Specialty
from schemas.specialty import SpecialtyCreate, SpecialtyUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_specialties(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Specialty]:
    """Obtiene una lista de especialidades."""
    return await crud_specialty.get_specialties(db, skip=skip, limit=limit)


async def create_specialty(
    db: AsyncSession, *, specialty_in: SpecialtyCreate, user_id: uuid.UUID
) -> Specialty:
    """Crea una nueva especialidad y maneja conflictos."""
    try:
        return await crud_specialty.create_specialty(
            db=db, specialty_in=specialty_in, user_id=user_id
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Una especialidad con este nombre ya existe.",
        )


async def get_specialty(db: AsyncSession, *, specialty_id: uuid.UUID) -> Specialty:
    """Obtiene una especialidad por ID, lanzando un error si no se encuentra."""
    db_specialty = await crud_specialty.get_specialty(db=db, specialty_id=specialty_id)
    if not db_specialty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Especialidad no encontrada."
        )
    return db_specialty


async def update_specialty(
    db: AsyncSession,
    *,
    specialty_id: uuid.UUID,
    specialty_in: SpecialtyUpdate,
    user_id: uuid.UUID,
) -> Specialty:
    """Actualiza una especialidad, verificando primero su existencia."""
    db_specialty = await get_specialty(db=db, specialty_id=specialty_id)
    return await crud_specialty.update_specialty(
        db=db, db_specialty=db_specialty, specialty_in=specialty_in, user_id=user_id
    )


async def remove_specialty(db: AsyncSession, *, specialty_id: uuid.UUID) -> Specialty:
    """Elimina una especialidad, verificando primero su existencia."""
    await get_specialty(db=db, specialty_id=specialty_id)
    deleted_specialty = await crud_specialty.remove_specialty(
        db=db, specialty_id=specialty_id
    )
    return deleted_specialty
