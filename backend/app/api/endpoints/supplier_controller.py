import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import require_permission
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.supplier import Supplier, SupplierCreate, SupplierUpdate
from service.supplier_service import supplier_service

router = APIRouter(tags=["Suppliers"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
require_supplier_create = Depends(require_permission("supplier:create"))
require_supplier_update = Depends(require_permission("supplier:update"))
require_supplier_delete = Depends(require_permission("supplier:delete"))


@router.get("/", response_model=ApiResponse[list[Supplier]])
async def read_suppliers(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Retrieve suppliers.
    """
    suppliers = await supplier_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=suppliers)


@router.post(
    "/", response_model=ApiResponse[Supplier], status_code=status.HTTP_201_CREATED
)
async def create_supplier(
    *,
    db: AsyncSession = db_dependency,
supplier_in: SupplierCreate,
    current_user: UserModel = require_supplier_create,
    ) -> Any:
    """
    Create new supplier.
    """
    supplier = await supplier_service.create(db, obj_in=supplier_in)
    return create_api_response(
        data=supplier,
        status_code=status.HTTP_201_CREATED,
        message="Supplier created successfully.",
    )


@router.get("/{supplier_id}", response_model=ApiResponse[Supplier])
async def read_supplier_by_id(
    supplier_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Get a specific supplier by ID.
    """
    supplier = await supplier_service.get_by_id(db, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return create_api_response(data=supplier)


@router.put("/{supplier_id}", response_model=ApiResponse[Supplier])
async def update_supplier(
    *,
    db: AsyncSession = db_dependency,
    supplier_id: uuid.UUID,
supplier_in: SupplierUpdate,
    current_user: UserModel = require_supplier_update,
    ) -> Any:
    """
    Update a supplier.
    """
    supplier = await supplier_service.update(db, id=supplier_id, obj_in=supplier_in)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return create_api_response(data=supplier, message="Supplier updated successfully.")


@router.delete("/{supplier_id}", response_model=ApiResponse[Supplier])
async def delete_supplier(
    *,
    db: AsyncSession = db_dependency,
supplier_id: uuid.UUID,
    current_user: UserModel = require_supplier_delete,
    ) -> Any:
    """
    Delete a supplier.
    """
    supplier = await supplier_service.delete(db, id=supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return create_api_response(data=supplier, message="Supplier deleted successfully.")
