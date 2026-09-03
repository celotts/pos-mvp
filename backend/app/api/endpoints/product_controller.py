import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import require_permission
from api.response_factory import ApiResponse, create_api_response
from core.i18n import tr
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.product import Product, ProductCreate, ProductUpdate
from service.product_service import product_service

router = APIRouter(tags=["Products"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
require_product_create = Depends(require_permission("product:create"))
require_product_update = Depends(require_permission("product:update"))
require_product_delete = Depends(require_permission("product:delete"))


@router.get("/", response_model=ApiResponse[list[Product]])
async def read_products(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Retrieve products (paginado). `data` es la lista y `total` el conteo global,
    de modo que el cliente pueda paginar.
    """
    products, total = await product_service.search(
        db=db, search=None, skip=skip, limit=limit
    )
    return create_api_response(data=products, total=total)


@router.get("/search", response_model=ApiResponse[list[Product]])
async def search_products(
    q: str = "",
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Búsqueda server-side por nombre o SKU (parcial, insensible a mayúsculas)
    con paginación. Devuelve `{"data": [...], "total": N}`.
    """
    products, total = await product_service.search(
        db=db, search=q, skip=skip, limit=limit
    )
    return create_api_response(data=products, total=total)


@router.post(
    "/", response_model=ApiResponse[Product], status_code=status.HTTP_201_CREATED
)
async def create_product(
    *,
    db: AsyncSession = db_dependency,
product_in: ProductCreate,
    current_user: UserModel = require_product_create,
    ) -> Any:
    """
    Create new product.
    """
    product = await product_service.create(
        db=db, obj_in=product_in, current_user=current_user
    )
    return create_api_response(
        data=product,
        status_code=status.HTTP_201_CREATED,
        message="Product created successfully.",
    )


@router.get("/{id}", response_model=ApiResponse[Product])
async def read_product_by_id(
    id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """
    Get a specific product by ID.
    """
    product = await product_service.get_by_id(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail=tr("NOT_FOUND.PRODUCT"))
    return create_api_response(data=product)


@router.put("/{id}", response_model=ApiResponse[Product])
async def update_product(
    *,
    db: AsyncSession = db_dependency,
    id: uuid.UUID,
product_in: ProductUpdate,
    current_user: UserModel = require_product_update,
    ) -> Any:
    """
    Update a product.
    """
    product = await product_service.update(
        db=db, id=id, obj_in=product_in, current_user=current_user
    )
    if not product:
        raise HTTPException(status_code=404, detail=tr("NOT_FOUND.PRODUCT"))
    return create_api_response(data=product, message="Product updated successfully.")


@router.delete("/{id}", response_model=ApiResponse[Product])
async def delete_product(
    *,
    db: AsyncSession = db_dependency,
id: uuid.UUID,
    current_user: UserModel = require_product_delete,
    ) -> Any:
    """
    Delete a product.
    """
    product = await product_service.delete(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail=tr("NOT_FOUND.PRODUCT"))
    return create_api_response(data=product, message="Product deleted successfully.")
