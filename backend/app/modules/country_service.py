import uuid

from core import crud_country
from fastapi import HTTPException, status
from models.country import Country
from schemas.country import CountryCreate, CountryUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def create_country(
    db: AsyncSession, *, country_in: CountryCreate, user_id: uuid.UUID
) -> Country:
    """Crea un país y maneja la lógica de negocio, como la duplicidad."""
    try:
        country = await crud_country.create_country(
            db=db, country_in=country_in, user_id=user_id
        )
        return country
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un país con ese nombre o código ISO ya existe.",
        )


async def get_countries(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Country]:
    """Obtiene una lista de países."""
    return await crud_country.get_countries(db, skip=skip, limit=limit)


async def get_country(db: AsyncSession, *, country_id: uuid.UUID) -> Country:
    """Obtiene un país por ID, manejando el caso de no encontrarlo."""
    db_country = await crud_country.get_country(db=db, country_id=country_id)
    if not db_country:
        raise HTTPException(status_code=404, detail="País no encontrado.")
    return db_country


async def update_country(
    db: AsyncSession,
    *,
    country_id: uuid.UUID,
    country_in: CountryUpdate,
    user_id: uuid.UUID,
) -> Country:
    """Actualiza un país, verificando primero su existencia."""
    db_country = await get_country(db=db, country_id=country_id)
    return await crud_country.update_country(
        db=db, db_country=db_country, country_in=country_in, user_id=user_id
    )


async def remove_country(db: AsyncSession, *, country_id: uuid.UUID) -> Country:
    """Elimina un país, verificando primero su existencia."""
    await get_country(db=db, country_id=country_id)  # Asegura que existe
    deleted_country = await crud_country.remove_country(db=db, country_id=country_id)
    return deleted_country
