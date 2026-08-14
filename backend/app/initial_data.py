import logging
import uuid

from core import (
    base,  # noqa: F401 - Importa todos los modelos para que Base los reconozca
)
from core.config import settings
from core.crud_user import crud_user
from core.db import async_session_maker
from models.role import Role
from schemas.user import UserCreate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ID del rol SUPER_ADMIN definido en V1__initial_schema.sql
SUPER_ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


async def init_db(db: AsyncSession) -> None:
    # Esta función es llamada al iniciar la aplicación para crear el primer superusuario

    # 1. Crear el rol de superusuario si no existe
    try:
        logger.info("Creando rol de Administrador inicial...")
        admin_role = Role(
            id=SUPER_ADMIN_ROLE_ID,  # Este es el SUPER_ADMIN
            name="ADMIN",
        )
        db.add(admin_role)
        await db.commit()
        logger.info("Rol de Administrador creado.")
    except IntegrityError:
        await db.rollback()
        logger.info("El rol de Administrador ya existe, omitiendo creación.")

    # 2. Crear el superusuario si no existe
    # Se asume que get_multi puede filtrar por email.
    users = await crud_user.get_multi(db, limit=1, email=settings.FIRST_SUPERUSER_EMAIL)
    if not users:
        logger.info("Creando superusuario inicial...")
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_FULL_NAME,
            role_id=SUPER_ADMIN_ROLE_ID,
        )
        await crud_user.create(db=db, obj_in=user_in)
        logger.info("Superusuario creado.")
    else:
        logger.info("El superusuario ya existe, omitiendo creación.")


async def main() -> None:
    logger.info("Iniciando la inicialización de la base de datos...")
    async with async_session_maker() as session:
        await init_db(session)
    logger.info("Inicialización de la base de datos completada.")
