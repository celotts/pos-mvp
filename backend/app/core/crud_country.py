import uuid

from models.country import Country
from schemas.country import CountryCreate, CountryUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_country(db: AsyncSession, country_id: uuid.UUID) -> Country | None:
    """Obtiene un país por su ID."""
    return await db.get(Country, country_id)


async def get_countries(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Country]:
    """Obtiene una lista de países."""
    result = await db.execute(select(Country).offset(skip).limit(limit))
    return result.scalars().all()


async def create_country(
    db: AsyncSession, *, country_in: CountryCreate, user_id: uuid.UUID
) -> Country:
    """Crea un nuevo país."""
    db_country = Country(
        **country_in.model_dump(),
        created_by=user_id,
    )
    db.add(db_country)
    await db.commit()
    await db.refresh(db_country)
    return db_country


async def update_country(
    db: AsyncSession,
    *,
    db_country: Country,
    country_in: CountryUpdate,
    user_id: uuid.UUID,
) -> Country:
    """Actualiza un país."""
    update_data = country_in.model_dump(exclude_unset=True)
    update_data["updated_by"] = user_id
    for field, value in update_data.items():
        setattr(db_country, field, value)
    await db.commit()
    await db.refresh(db_country)
    return db_country


async def remove_country(db: AsyncSession, *, country_id: uuid.UUID) -> Country | None:
    """Elimina un país (marcado lógico)."""
    db_country = await get_country(db, country_id)
    if db_country:
        # En lugar de db.delete, podrías implementar borrado lógico aquí
        await db.delete(db_country)
        await db.commit()
    return db_country
