import logging
import os

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("initial_data")


async def init_db(db: AsyncSession):
    """
    Inicializa la base de datos ejecutando scripts SQL desde el directorio /script_data.
    """
    logger.info("Iniciando inicialización de la base de datos...")
    script_dir = "/script_data"

    if not os.path.isdir(script_dir):
        logger.warning(
            f"Directorio de scripts no encontrado en {script_dir}, omitiendo."
        )
        return

    scripts = sorted([f for f in os.listdir(script_dir) if f.endswith(".sql")])

    # Para ejecutar scripts DDL con múltiples sentencias, debemos evitar el
    # mecanismo de "prepared statements" de SQLAlchemy/asyncpg.
    # La forma correcta es obtener la conexión "raw" de asyncpg y usar su
    # método `execute`, que sí maneja scripts completos.
    try:
        connection = await db.connection()
        raw_dbapi_connection = await connection.get_raw_connection()
        asyncpg_connection = raw_dbapi_connection.driver_connection

        for script_name in scripts:
            script_path = os.path.join(script_dir, script_name)
            logger.info(f"Ejecutando script: {script_name}")
            async with aiofiles.open(script_path, "r", encoding="utf-8") as f:
                script_content = await f.read()
                await asyncpg_connection.execute(script_content)

    except Exception as e:
        logger.error(f"Error durante la inicialización de la base de datos: {e}")
        raise

    logger.info("Inicialización de la base de datos completada.")
