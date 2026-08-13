import uuid
from typing import Any

from api.deps import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from modules.supplier_service import supplier_service
from schemas.supplier import Supplier, SupplierCreate, SupplierUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/suppliers", tags=["suppliers"])

db_dependency = Depends(get_db)


@router.get("/", response_model=list[Supplier])
async def read_suppliers(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve suppliers.
    """
    suppliers = await supplier_service.get_all(db, skip=skip, limit=limit)
    return suppliers


@router.post("/", response_model=Supplier, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    *,
    db: AsyncSession = db_dependency,
    supplier_in: SupplierCreate,
) -> Any:
    """
    Create new supplier.
    """
    supplier = await supplier_service.create(db, obj_in=supplier_in)
    return supplier


@router.get("/{supplier_id}", response_model=Supplier)
async def read_supplier_by_id(
    supplier_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """
    Get a specific supplier by ID.
    """
    supplier = await supplier_service.get_by_id(db, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.put("/{supplier_id}", response_model=Supplier)
async def update_supplier(
    *,
    db: AsyncSession = db_dependency,
    supplier_id: uuid.UUID,
    supplier_in: SupplierUpdate,
) -> Any:
    """
    Update a supplier.
    """
    supplier = await supplier_service.update(db, id=supplier_id, obj_in=supplier_in)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier
