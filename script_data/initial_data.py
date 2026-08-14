import asyncio
import logging
import sys
from pathlib import Path

# Añade el directorio raíz del proyecto a sys.path para permitir importaciones absolutas
# Esto hace que el script se pueda ejecutar de forma independiente
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.crud_role import crud_role
from backend.app.core.crud_user import crud_user
from backend.app.core.db import async_session_maker
from backend.app.schemas.role import RoleCreate
from backend.app.schemas.user import UserCreate

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
        # Llama al método 'create' de la clase base, que es el correcto
        admin_role = await crud_role.create(db=db, obj_in=role_in)
        logger.info("Rol creado.")

    # 2. Crear superusuario si no existe
    # Se asume que get_multi puede filtrar por email.
    users = await crud_user.get_multi(db, limit=1, email=settings.FIRST_SUPERUSER_EMAIL)
    if not users:
        logger.info("Creando superusuario inicial...")
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_FULL_NAME,
            role_id=admin_role.id,  # Usar el ID del rol que acabamos de obtener/crear
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


if __name__ == "__main__":
    asyncio.run(main())
