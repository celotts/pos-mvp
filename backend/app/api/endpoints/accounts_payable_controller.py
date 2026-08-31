import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from models.user import User as UserModel
from schemas.accounts_payable import (AccountsPayable, AccountsPayableCreate,
                                      AccountsPayableUpdate)
from service.accounts_payable_service import accounts_payable_service

router = APIRouter(tags=["Accounting"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
get_current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[AccountsPayable],
    status_code=status.HTTP_201_CREATED,
    summary="Create an Account Payable",
)
async def create_account_payable(
    *,
    account_in: AccountsPayableCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Creates a new accounts payable record, usually associated with a purchase."""
    new_account = await accounts_payable_service.create(db=db, obj_in=account_in)
    return create_api_response(
        data=new_account,
        status_code=status.HTTP_201_CREATED,
        message="Account payable created successfully.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[AccountsPayable]],
    summary="Get list of Accounts Payable",
)
async def read_accounts_payable(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets a list of all accounts payable."""
    accounts = await accounts_payable_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=accounts)


@router.get(
    "/{account_id}",
    response_model=ApiResponse[AccountsPayable],
    summary="Get an Account Payable by ID",
)
async def read_account_payable_by_id(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Gets the details of a specific account payable."""
    account = await accounts_payable_service.get(db, id=account_id)
    return create_api_response(data=account)


@router.put(
    "/{account_id}",
    response_model=ApiResponse[AccountsPayable],
    summary="Update an Account Payable",
)
async def update_account_payable(
    *,
    account_id: uuid.UUID,
    account_in: AccountsPayableUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Updates the data of an account payable (e.g., to register a payment)."""
    updated_account = await accounts_payable_service.update(
        db=db, id=account_id, obj_in=account_in
    )
    if not updated_account:
        raise HTTPException(status_code=404, detail="Account payable not found.")
    return create_api_response(
        data=updated_account, message="Account payable updated successfully."
    )


@router.delete(
    "/{account_id}",
    response_model=ApiResponse[AccountsPayable],
    summary="Delete an Account Payable",
)
async def delete_account_payable(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = get_current_admin_user_dependency,
) -> Any:
    """Deletes an account payable record."""
    deleted_account = await accounts_payable_service.remove(db, id=account_id)
    if not deleted_account:
        raise HTTPException(status_code=404, detail="Account payable not found.")
    return create_api_response(
        data=deleted_account, message="Account payable deleted successfully."
    )
