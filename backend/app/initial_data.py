import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from core import base  # noqa: F401 - Importa todos los modelos para que Base los reconozca
from core import crud_user
from core.config import settings
from core.db import async_session_maker, engine, Base
from models.role import Role
from schemas.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ID del rol SUPER_ADMIN definido en init.sql
SUPER_ADMIN_ROLE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


async def init_db(db: AsyncSession) -> None:
    # Esta función es llamada al iniciar la aplicación para crear el primer superusuario

    # 1. Asegurarse de que los roles existan
    admin_role = await db.get(Role, SUPER_ADMIN_ROLE_ID)
    if not admin_role:
        logger.info("Creando rol de Administrador inicial...")
        admin_role = Role(
            id=SUPER_ADMIN_ROLE_ID,
            name="ADMIN",
        )
        db.add(admin_role)
        # Puedes añadir más roles aquí si es necesario
        # db.add(Role(id=uuid.uuid4(), name="USER", description="Rol de usuario estándar."))
        await db.commit()
        await db.refresh(
            admin_role
        )  # Refresca la instancia para obtener los valores de la BD
        logger.info("Roles iniciales creados.")

    # 2. Crear el superusuario si no existe
    user = await crud_user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        logger.info("Creando superusuario inicial...")
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin",
            role_id=SUPER_ADMIN_ROLE_ID,
        )
        await crud_user.create_user(db, user_in=user_in)
        logger.info("Superusuario creado.")
    else:
        logger.info("El superusuario ya existe, omitiendo creación.")


async def main() -> None:
    logger.info("Iniciando la inicialización de la base de datos...")
    async with async_session_maker() as session:
        await init_db(session)
    logger.info("Inicialización de la base de datos completada.")
