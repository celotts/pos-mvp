import asyncio
import logging

from core import crud_user
from core.config import settings
from core.crud_role import crud_role
from core.db import async_session_maker
from schemas.role import RoleCreate
from schemas.user import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    """
    Inicializa la base de datos creando el primer superusuario si no existe.
    """
    # 1. Crear roles si no existen
    admin_role_name = "SUPER_ADMIN"
    admin_role = await crud_role.get_by_name(db, name=admin_role_name)
    if not admin_role:
        logger.info(f"Creando rol '{admin_role_name}'...")
        role_in = RoleCreate(
            name=admin_role_name, description="Super Administrator Role"
        )
        admin_role = await crud_role.create(db, obj_in=role_in)
        logger.info("Rol creado.")

    # 2. Crear superusuario si no existe
    user = await crud_user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        logger.info("Creando superusuario inicial...")
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_FULL_NAME,
            role_id=admin_role.id,  # Usar el ID del rol que acabamos de obtener/crear
        )
        await crud_user.create(db, obj_in=user_in)
        logger.info("Superusuario creado.")
    else:
        logger.info("El superusuario ya existe, omitiendo creación.")


async def main() -> None:
    logger.info("Iniciando la inicialización de la base de datos...")
    async with async_session_maker() as session:
        await init_db(session)
    logger.info("Inicialización de la base de datos completada.")


if __name__ == "__main__":
    asyncio.run(main())
