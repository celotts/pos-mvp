import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import async_session_maker
from core import crud_user
from schemas.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    """
    Inicializa la base de datos creando el primer superusuario si no existe.
    """
    # Busca el rol de administrador. Asumimos que ya fue creado por los scripts SQL.
    # Si no, puedes añadir la lógica para crearlo aquí.
    # Por ahora, usaremos un UUID fijo para el rol de admin como en tus scripts.
    admin_role_id = "00000000-0000-0000-0000-000000000001"

    user = await crud_user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        logger.info("Creando superusuario inicial...")
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name="Admin",
            role_id=admin_role_id,
        )
        await crud_user.create_user(db, user_in=user_in)
        logger.info("Superusuario creado.")
    else:
        logger.info("El superusuario ya existe, omitiendo creación.")


async def main() -> None:
    logger.info("Iniciando la inicialización de la base deatos...")
    async with async_session_maker() as session:
        await init_db(session)
    logger.info("Inicialización de la base de datos completada.")


if __name__ == "__main__":
    asyncio.run(main())
