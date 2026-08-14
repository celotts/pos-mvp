import uuid
from typing import Any

from api.deps import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from modules.product_service import product_service
from schemas.product import Product, ProductCreate, ProductUpdate
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/products", tags=["products"])

db_dependency = Depends(get_db)


@router.get("/", response_model=list[Product])
async def read_products(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve products.
    """
    products = await product_service.get_all(db=db, skip=skip, limit=limit)
    return products


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    *,
    db: AsyncSession = db_dependency,
    product_in: ProductCreate,
) -> Any:
    """
    Create new product.
    """
    product = await product_service.create(db, obj_in=product_in)
    return product


@router.get("/{id}", response_model=Product)
async def read_product_by_id(
    id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """
    Get a specific product by ID.
    """
    product = await product_service.get_by_id(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{id}", response_model=Product)
async def update_product(
    *,
    db: AsyncSession = db_dependency,
    id: uuid.UUID,
    product_in: ProductUpdate,
) -> Any:
    """
    Update a product.
    """
    product = await product_service.update(db=db, id=id, obj_in=product_in)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{id}", response_model=Product)
async def delete_product(
    *,
    db: AsyncSession = db_dependency,
    id: uuid.UUID,
) -> Any:
    """
    Delete a product.
    """
    product = await product_service.delete(db=db, id=id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
