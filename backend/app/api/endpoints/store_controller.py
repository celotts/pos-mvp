import uuid
from typing import Any

from api.deps import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from modules.store_service import store_service
from schemas.store import Store, StoreCreate, StoreUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/stores", tags=["stores"])

db_dependency = Depends(get_db)


@router.get("/", response_model=list[Store])
async def read_stores(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve stores.
    """
    stores = await store_service.get_all(db, skip=skip, limit=limit)
    return stores


@router.post("/", response_model=Store, status_code=status.HTTP_201_CREATED)
async def create_store(
    *,
    db: AsyncSession = db_dependency,
    store_in: StoreCreate,
) -> Any:
    """
    Create new store.
    """
    store = await store_service.create(db, obj_in=store_in)
    return store


@router.get("/{store_id}", response_model=Store)
async def read_store_by_id(
    store_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """
    Get a specific store by ID.
    """
    store = await store_service.get_by_id(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.put("/{store_id}", response_model=Store)
async def update_store(
    *, db: AsyncSession = db_dependency, store_id: uuid.UUID, store_in: StoreUpdate
) -> Any:
    """
    Update a store.
    """
    store = await store_service.update(db, id=store_id, obj_in=store_in)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store
