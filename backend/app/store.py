import uuid
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_admin_user, get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import store_service
from schemas.store import Store, StoreCreate, StoreUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[Store],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva Tienda",
)
async def create_store(
    *,
    store_in: StoreCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Crea una nueva tienda."""
    store = await store_service.create_store(
        db=db, store_in=store_in, current_user=current_user
    )
    return create_api_response(
        data=store,
        status_code=status.HTTP_201_CREATED,
        message="Tienda creada con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[Store]],
    summary="Obtener una lista de Tiendas",
)
async def read_stores(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtiene una lista paginada de tiendas."""
    stores = await store_service.get_stores(db, skip=skip, limit=limit)
    return create_api_response(data=stores)


@router.get(
    "/{store_id}",
    response_model=ApiResponse[Store],
    summary="Obtener una Tienda por ID",
)
async def read_store(
    *,
    store_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Obtiene una tienda específica por su ID."""
    store = await store_service.get_store(db, store_id=store_id)
    return create_api_response(data=store)


@router.put(
    "/{store_id}",
    response_model=ApiResponse[Store],
    summary="Actualizar una Tienda",
)
async def update_store(
    *,
    store_id: uuid.UUID,
    store_in: StoreUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Actualiza una tienda por su ID."""
    updated_store = await store_service.update_store(
        db=db, store_id=store_id, store_in=store_in, current_user=current_user
    )
    return create_api_response(
        data=updated_store, message="Tienda actualizada con éxito."
    )


@router.delete(
    "/{store_id}", response_model=ApiResponse[Store], summary="Eliminar una Tienda"
)
async def delete_store(
    *,
    store_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Elimina una tienda por su ID."""
    deleted_store = await store_service.remove_store(db, store_id=store_id)
    return create_api_response(
        data=deleted_store, message="Tienda eliminada con éxito."
    )
