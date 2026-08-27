import uuid

from core.crud_cash_account import crud_cash_account
from fastapi import HTTPException, status
from models import CashAccount
from models import User as UserModel
from schemas.cash_account import CashAccountCreate, CashAccountUpdate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


async def get_cash_accounts(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[CashAccount]:
    """Obtiene una lista de cuentas de caja/banco."""
    return await crud_cash_account.get_multi(db, skip=skip, limit=limit)


async def create_cash_account(
    db: AsyncSession, *, account_in: CashAccountCreate, current_user: UserModel
) -> CashAccount:
    """Crea una nueva cuenta de caja/banco."""
    try:
        return await crud_cash_account.create(
            db=db,
            obj_in=account_in,
            created_by=current_user.id,
            created_by_role_id=current_user.role_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this name already exists.",
        )


async def get_cash_account(db: AsyncSession, *, account_id: uuid.UUID) -> CashAccount:
    """Obtiene una cuenta por ID."""
    db_account = await crud_cash_account.get(db=db, id=account_id)
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found."
        )
    return db_account


async def update_cash_account(
    db: AsyncSession,
    *,
    account_id: uuid.UUID,
    account_in: CashAccountUpdate,
    current_user: UserModel,
) -> CashAccount:
    """Actualiza una cuenta."""
    db_account = await get_cash_account(db=db, account_id=account_id)
    return await crud_cash_account.update(
        db=db,
        db_obj=db_account,
        obj_in=account_in,
        updated_by=current_user.id,
        updated_by_role_id=current_user.role_id,
    )


async def remove_cash_account(
    db: AsyncSession, *, account_id: uuid.UUID
) -> CashAccount:
    """Elimina una cuenta."""
    await get_cash_account(db=db, account_id=account_id)
    return await crud_cash_account.remove(db=db, id=account_id)
