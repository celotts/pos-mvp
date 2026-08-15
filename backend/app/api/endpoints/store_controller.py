import uuid
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, HTTPException, status
from models.user import User as UserModel
from modules.store_service import store_service
from schemas.store import Store, StoreCreate, StoreUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Stores"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.get("/", response_model=ApiResponse[list[Store]])
async def read_stores(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Retrieve stores.
    """
    stores = await store_service.get_all(db=db, skip=skip, limit=limit)
    return create_api_response(data=stores)


@router.post(
    "/", response_model=ApiResponse[Store], status_code=status.HTTP_201_CREATED
)
async def create_store(
    *,
    db: AsyncSession = db_dependency,
    store_in: StoreCreate,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Create new store.
    """
    store = await store_service.create(db=db, obj_in=store_in)
    return create_api_response(
        data=store,
        status_code=status.HTTP_201_CREATED,
        message="Tienda creada con éxito.",
    )


@router.get("/{store_id}", response_model=ApiResponse[Store])
async def read_store_by_id(
    store_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Get a specific store by ID.
    """
    store = await store_service.get_by_id(db=db, id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return create_api_response(data=store)


@router.put("/{store_id}", response_model=ApiResponse[Store])
async def update_store(
    *,
    db: AsyncSession = db_dependency,
    store_id: uuid.UUID,
    store_in: StoreUpdate,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Update a store.
    """
    store = await store_service.update(db=db, id=store_id, obj_in=store_in)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return create_api_response(data=store, message="Tienda actualizada con éxito.")


@router.delete("/{store_id}", response_model=ApiResponse[Store])
async def delete_store(
    *,
    db: AsyncSession = db_dependency,
    store_id: uuid.UUID,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Delete a store.
    """
    store = await store_service.delete(db=db, id=store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return create_api_response(data=store, message="Tienda eliminada con éxito.")
