import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.accounts_receivable import (
    AccountsReceivable,
    AccountsReceivableCreate,
    AccountsReceivableUpdate,
)
from service.accounts_receivable_service import accounts_receivable_service

router = APIRouter(tags=["Accounting"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
get_current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[AccountsReceivable],
    status_code=status.HTTP_201_CREATED,
    summary="Create an Account Receivable",
)
async def create_account_receivable(
    *,
    account_in: AccountsReceivableCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Creates a new accounts receivable record, usually associated with a sale."""
    new_account = await accounts_receivable_service.create(db=db, obj_in=account_in)
    return create_api_response(
        data=new_account,
        status_code=status.HTTP_201_CREATED,
        message="Account receivable created successfully.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[AccountsReceivable]],
    summary="Get list of Accounts Receivable",
)
async def read_accounts_receivable(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets a list of all accounts receivable."""
    accounts = await accounts_receivable_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=accounts)


@router.get(
    "/{account_id}",
    response_model=ApiResponse[AccountsReceivable],
    summary="Get an Account Receivable by ID",
)
async def read_account_receivable_by_id(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets the details of a specific account receivable."""
    account = await accounts_receivable_service.get(db, id=account_id)
    return create_api_response(data=account)


@router.put(
    "/{account_id}",
    response_model=ApiResponse[AccountsReceivable],
    summary="Update an Account Receivable",
)
async def update_account_receivable(
    *,
    account_id: uuid.UUID,
    account_in: AccountsReceivableUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Updates the data of an account receivable (e.g., to register a payment)."""
    updated_account = await accounts_receivable_service.update(
        db=db, id=account_id, obj_in=account_in
    )
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account receivable not found.")
    return create_api_response(
        data=updated_account, message="Account receivable updated successfully."
    )


@router.delete(
    "/{account_id}",
    response_model=ApiResponse[AccountsReceivable],
    summary="Delete an Account Receivable",
)
async def delete_account_receivable(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Deletes an account receivable record."""
    deleted_account = await accounts_receivable_service.remove(db, id=account_id)
    if not deleted_account:
        raise HTTPException(status_code=404, detail="Account receivable not found.")
    return create_api_response(
        data=deleted_account, message="Account receivable deleted successfully."
    )
