import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.cash_account import (
    CashAccount,
    CashAccountCreate,
    CashAccountUpdate,
)
from service import cash_account_service

router = APIRouter(tags=["Accounting"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[CashAccount],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Cash/Bank Account",
)
async def create_cash_account(
    *,
    account_in: CashAccountCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Creates a new cash or bank account."""
    account = await cash_account_service.create_cash_account(
        db=db, account_in=account_in, current_user=current_user
    )
    return create_api_response(
        data=account,
        status_code=status.HTTP_201_CREATED,
        message="Account created successfully.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[CashAccount]],
    summary="Get a list of Accounts",
)
async def read_cash_accounts(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    _current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets a paginated list of accounts."""
    accounts = await cash_account_service.get_cash_accounts(db, skip=skip, limit=limit)
    return create_api_response(data=accounts)


@router.get(
    "/{account_id}",
    response_model=ApiResponse[CashAccount],
    summary="Get an Account by ID",
)
async def read_cash_account(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    _current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets a specific account by its ID."""
    account = await cash_account_service.get_cash_account(db, account_id=account_id)
    return create_api_response(data=account)


@router.put(
    "/{account_id}",
    response_model=ApiResponse[CashAccount],
    summary="Update an Account",
)
async def update_cash_account(
    *,
    account_id: uuid.UUID,
    account_in: CashAccountUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Updates an account by its ID."""
    updated_account = await cash_account_service.update_cash_account(
        db=db, account_id=account_id, account_in=account_in, current_user=current_user
    )
    return create_api_response(
        data=updated_account, message="Account updated successfully."
    )


@router.delete(
    "/{account_id}",
    response_model=ApiResponse[CashAccount],
    summary="Delete an Account",
)
async def delete_cash_account(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Deletes an account by its ID."""
    deleted_account = await cash_account_service.remove_cash_account(
        db, account_id=account_id
    )
    return create_api_response(
        data=deleted_account, message="Account deleted successfully."
    )
