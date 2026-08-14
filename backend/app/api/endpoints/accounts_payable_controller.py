import uuid
from typing import Any

from api.response_factory import ApiResponse, create_api_response
from dependencies import get_current_user, get_db
from fastapi import APIRouter, Depends, status
from models.user import User as UserModel
from modules.accounts_payable_service import accounts_payable_service
from schemas.accounts_payable import (
    AccountsPayable,
    AccountsPayableCreate,
    AccountsPayableUpdate,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

db_dependency = Depends(get_db)
current_user_dependency = Depends(get_current_user)


@router.post(
    "/",
    response_model=ApiResponse[AccountsPayable],
    status_code=status.HTTP_201_CREATED,
    summary="Crear una Cuenta por Pagar",
)
async def create_account_payable(
    *,
    account_in: AccountsPayableCreate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Crea un nuevo registro de cuenta por pagar, generalmente asociado a una compra."""
    new_account = await accounts_payable_service.create(db=db, obj_in=account_in)
    return create_api_response(
        data=new_account,
        status_code=status.HTTP_201_CREATED,
        message="Cuenta por pagar creada con éxito.",
    )


@router.get(
    "/",
    response_model=ApiResponse[list[AccountsPayable]],
    summary="Obtener lista de Cuentas por Pagar",
)
async def read_accounts_payable(
    db: AsyncSession = db_dependency,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Obtiene una lista de todas las cuentas por pagar."""
    accounts = await accounts_payable_service.get_all(db, skip=skip, limit=limit)
    return create_api_response(data=accounts)


@router.get(
    "/{account_id}",
    response_model=ApiResponse[AccountsPayable],
    summary="Obtener una Cuenta por Pagar por ID",
)
async def read_account_payable_by_id(
    *,
    account_id: uuid.UUID,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Obtiene los detalles de una cuenta por pagar específica."""
    account = await accounts_payable_service.get(db, id=account_id)
    return create_api_response(data=account)


@router.put(
    "/{account_id}",
    response_model=ApiResponse[AccountsPayable],
    summary="Actualizar una Cuenta por Pagar",
)
async def update_account_payable(
    *,
    account_id: uuid.UUID,
    account_in: AccountsPayableUpdate,
    db: AsyncSession = db_dependency,
    current_user: UserModel = current_user_dependency,
) -> Any:
    """Actualiza los datos de una cuenta por pagar (ej. para registrar un pago)."""
    updated_account = await accounts_payable_service.update(
        db=db, id=account_id, obj_in=account_in
    )
    return create_api_response(
        data=updated_account, message="Cuenta por pagar actualizada con éxito."
    )
