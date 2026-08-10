import uuid

from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_customer(db: AsyncSession, customer_id: uuid.UUID) -> Customer | None:
    """Obtiene un cliente por su ID."""
    result = await db.execute(select(Customer).filter(Customer.id == customer_id))
    return result.scalars().first()


async def get_customers(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Customer]:
    """Obtiene una lista de clientes con paginación."""
    result = await db.execute(select(Customer).offset(skip).limit(limit))
    return result.scalars().all()


async def create_customer(
    db: AsyncSession, *, customer_in: CustomerCreate, user_id: uuid.UUID
) -> Customer:
    """Crea un nuevo cliente."""
    db_customer = Customer(
        **customer_in.model_dump(),
        created_by=user_id,
    )
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer


async def update_customer(
    db: AsyncSession,
    *,
    db_customer: Customer,
    customer_in: CustomerUpdate,
    user_id: uuid.UUID,
) -> Customer:
    """Actualiza un cliente."""
    update_data = customer_in.model_dump(exclude_unset=True)
    update_data["updated_by"] = user_id
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer


async def remove_customer(
    db: AsyncSession, *, customer_id: uuid.UUID
) -> Customer | None:
    """Elimina un cliente."""
    db_customer = await get_customer(db, customer_id)
    if db_customer:
        await db.delete(db_customer)
        await db.commit()
    return db_customer
