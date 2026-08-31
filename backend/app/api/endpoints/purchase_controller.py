import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.purchase import Purchase, PurchaseCreate, PurchaseUpdate
from service.purchase_service import purchase_service

router = APIRouter(tags=["Purchases"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
get_current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[Purchase],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Purchase",
)
async def create_purchase(
    *,
    purchase_in: PurchaseCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Creates a new purchase record from a supplier."""
    new_purchase = await purchase_service.create(db=db, obj_in=purchase_in)
    return create_api_response(
        data=new_purchase,
        status_code=status.HTTP_201_CREATED,
        message="Purchase created successfully.",
    )


@router.get(
    "/", response_model=ApiResponse[list[Purchase]], summary="Get list of Purchases"
)
async def read_purchases(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets a list of all purchases."""
    purchases = await purchase_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=purchases)


@router.get(
    "/{purchase_id}",
    response_model=ApiResponse[Purchase],
    summary="Get a Purchase by ID",
)
async def read_purchase_by_id(
    *,
    purchase_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets the details of a specific purchase."""
    purchase = await purchase_service.get(db, id=purchase_id)
    return create_api_response(data=purchase)


@router.put(
    "/{purchase_id}",
    response_model=ApiResponse[Purchase],
    summary="Update a Purchase",
)
async def update_purchase(
    *,
    purchase_id: uuid.UUID,
    purchase_in: PurchaseUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Updates the data of an existing purchase."""
    updated_purchase = await purchase_service.update(
        db=db, id=purchase_id, obj_in=purchase_in
    )
    return create_api_response(
        data=updated_purchase, message="Purchase updated successfully."
    )


@router.delete(
    "/{purchase_id}",
    response_model=ApiResponse[Purchase],
    summary="Delete a Purchase",
)
async def delete_purchase(
    *,
    purchase_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Deletes a purchase record."""
    deleted_purchase = await purchase_service.remove(db, id=purchase_id)
    return create_api_response(
        data=deleted_purchase, message="Purchase deleted successfully."
    )
