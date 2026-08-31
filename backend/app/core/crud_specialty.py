import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.specialty import Specialty
from schemas.specialty import SpecialtyCreate, SpecialtyUpdate


async def get_specialty(db: AsyncSession, specialty_id: uuid.UUID) -> Specialty | None:
    """Obtiene una especialidad por su ID."""
    result = await db.execute(select(Specialty).filter(Specialty.id == specialty_id))
    return result.scalars().first()


async def get_specialties(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Specialty]:
    """Obtiene una lista de especialidades con paginación."""
    result = await db.execute(select(Specialty).offset(skip).limit(limit))
    return result.scalars().all()


async def create_specialty(
    db: AsyncSession, *, specialty_in: SpecialtyCreate, user_id: uuid.UUID
) -> Specialty:
    """Crea una nueva especialidad."""
    db_specialty = Specialty(
        **specialty_in.model_dump(),
        created_by=user_id,
    )
    db.add(db_specialty)
    await db.commit()
    await db.refresh(db_specialty)
    return db_specialty


async def update_specialty(
    db: AsyncSession,
    *,
    db_specialty: Specialty,
    specialty_in: SpecialtyUpdate,
    user_id: uuid.UUID,
) -> Specialty:
    """Actualiza una especialidad."""
    update_data = specialty_in.model_dump(exclude_unset=True)
    update_data["updated_by"] = user_id
    for field, value in update_data.items():
        setattr(db_specialty, field, value)
    await db.commit()
    await db.refresh(db_specialty)
    return db_specialty


async def remove_specialty(
    db: AsyncSession, *, specialty_id: uuid.UUID
) -> Specialty | None:
    """Elimina una especialidad."""
    db_specialty = await get_specialty(db, specialty_id)
    if db_specialty:
        await db.delete(db_specialty)
        await db.commit()
    return db_specialty
