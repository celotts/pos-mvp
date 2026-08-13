from core import crud_customer
from fastapi import HTTPException, status
from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate
from sqlalchemy.ext.asyncio import AsyncSession


async def get_customers(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Customer]:
    """Obtiene una lista de clientes."""
    return await crud_customer.get_customers(db, skip=skip, limit=limit)


async def create_customer(db: AsyncSession, customer_in: CustomerCreate) -> Customer:
    """Crea un nuevo cliente."""
    return await crud_customer.create_customer(db=db, customer_in=customer_in)


async def get_customer(db: AsyncSession, customer_id: int) -> Customer:
    """Obtiene un cliente por ID, manejando el caso de no encontrarlo."""
    db_customer = await crud_customer.get_customer(db=db, customer_id=customer_id)
    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado."
        )
    return db_customer


async def update_customer(
    db: AsyncSession, customer_id: int, customer_in: CustomerCreate
) -> Customer:
    """Actualiza un cliente, verificando primero su existencia."""
    db_customer = await get_customer(db=db, customer_id=customer_id)
    return await crud_customer.update_customer(
        db=db, db_customer=db_customer, customer_in=customer_in
    )


async def delete_customer(db: AsyncSession, customer_id: int) -> None:
    """Elimina un cliente, verificando primero su existencia."""
    db_customer = await get_customer(db=db, customer_id=customer_id)
    await crud_customer.delete_customer(db=db, db_customer=db_customer)


async def get_customer_by_email(db: AsyncSession, email: str) -> Customer:
    """Obtiene un cliente por correo electrónico, manejando el caso de no encontrarlo."""
    db_customer = await crud_customer.get_customer_by_email(db=db, email=email)
    if not db_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado."
        )
    return db_customer


async def update_customer(
    db: AsyncSession, *, customer_id: int, customer_in: CustomerUpdate
) -> Customer:
    """Actualiza un cliente, verificando primero su existencia."""
    db_customer = await get_customer(db=db, customer_id=customer_id)
    return await crud_customer.update_customer(
        db=db, db_customer=db_customer, customer_in=customer_in
    )
