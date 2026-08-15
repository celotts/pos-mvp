import uuid
from typing import Any

from api.deps_auth import get_current_admin_user
from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules import cash_account_service
from schemas.cash_account import (
    CashAccount,
    CashAccountCreate,
    CashAccountUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Accounting"])

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)
current_admin_user_dependency = Depends(get_current_admin_user)


@router.post(
    "/",
    response_model=ApiResponse[CashAccount],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva Cuenta de Caja/Banco",
)
async def create_cash_account(
    *,
    account_in: CashAccountCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Crea una nueva cuenta de caja o banco."""
    account = await cash_account_service.create_cash_account(
        db=db, account_in=account_in, current_user=current_user
    )
    return create_api_response(
        data=account,
        status_code=status.HTTP_201_CREATED,
        message="Cuenta creada con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[CashAccount]],
    summary="Obtener una lista de Cuentas",
)
async def read_cash_accounts(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Obtiene una lista paginada de cuentas."""
    accounts = await cash_account_service.get_cash_accounts(db, skip=skip, limit=limit)
    return create_api_response(data=accounts)


@router.get(
    "/{account_id}",
    response_model=ApiResponse[CashAccount],
    summary="Obtener una Cuenta por ID",
)
async def read_cash_account(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
) -> Any:
    """Obtiene una cuenta específica por su ID."""
    account = await cash_account_service.get_cash_account(db, account_id=account_id)
    return create_api_response(data=account)


@router.put(
    "/{account_id}",
    response_model=ApiResponse[CashAccount],
    summary="Actualizar una Cuenta",
)
async def update_cash_account(
    *,
    account_id: uuid.UUID,
    account_in: CashAccountUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Actualiza una cuenta por su ID."""
    updated_account = await cash_account_service.update_cash_account(
        db=db, account_id=account_id, account_in=account_in, current_user=current_user
    )
    return create_api_response(
        data=updated_account, message="Cuenta actualizada con éxito."
    )


@router.delete(
    "/{account_id}",
    response_model=ApiResponse[CashAccount],
    summary="Eliminar una Cuenta",
)
async def delete_cash_account(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_admin_user_dependency,
) -> Any:
    """Elimina una cuenta por su ID."""
    deleted_account = await cash_account_service.remove_cash_account(
        db, account_id=account_id
    )
    return create_api_response(
        data=deleted_account, message="Cuenta eliminada con éxito."
    )
