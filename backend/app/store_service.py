import uuid

from core import crud_municipality, crud_store
from fastapi import HTTPException, status
from models import Store
from models import User as UserModel
from schemas.store import StoreCreate, StoreUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_stores(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Store]:
    """Obtiene una lista de tiendas."""
    return await crud_store.get_multi(db, skip=skip, limit=limit)


async def create_store(
    db: AsyncSession, *, store_in: StoreCreate, current_user: UserModel
) -> Store:
    """Crea una nueva tienda."""
    # Verifica que el municipio exista
    municipality = await crud_municipality.get(db, id=store_in.municipality_id)
    if not municipality:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El municipio con id '{store_in.municipality_id}' no existe.",
        )
    try:
        return await crud_store.create(
            db=db,
            obj_in=store_in,
            created_by=current_user.id,
            created_by_role_id=current_user.role_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Una tienda con este nombre o email ya existe.",
        )


async def get_store(db: AsyncSession, *, store_id: uuid.UUID) -> Store:
    """Obtiene una tienda por ID."""
    db_store = await crud_store.get(db=db, id=store_id)
    if not db_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tienda no encontrada."
        )
    return db_store


async def update_store(
    db: AsyncSession,
    *,
    store_id: uuid.UUID,
    store_in: StoreUpdate,
    current_user: UserModel,
) -> Store:
    """Actualiza una tienda."""
    db_store = await get_store(db=db, store_id=store_id)
    return await crud_store.update(
        db=db,
        db_obj=db_store,
        obj_in=store_in,
        updated_by=current_user.id,
        updated_by_role_id=current_user.role_id,
    )


async def remove_store(db: AsyncSession, *, store_id: uuid.UUID) -> Store:
    """Elimina una tienda."""
    await get_store(db=db, store_id=store_id)
    return await crud_store.remove(db=db, id=store_id)
