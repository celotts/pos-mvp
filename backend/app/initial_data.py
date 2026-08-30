import logging

from core.config import settings
from core.crud_role import crud_role
from core.crud_user import crud_user
from core.db import Base, async_session_maker, engine

# Import all models so that Base knows about them.
# This is a crucial step to ensure that SQLAlchemy's metadata is populated
# before `Base.metadata.create_all` is called.
from schemas.role import RoleCreate
from schemas.user import UserCreate
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Definiciones de Datos Iniciales ---
INITIAL_ROLES = [
    {
        "name": "SUPER_ADMIN",
        "description": "Super administrador con todos los permisos.",
    },
    {"name": "ADMIN", "description": "Administrador con la mayoría de los permisos."},
]


async def _create_initial_roles(db: AsyncSession):
    """Crea los roles fundamentales si no existen."""
    logger.info("Verificando y creando roles iniciales...")
    for role_data in INITIAL_ROLES:
        role = await crud_role.get_by_name(db, name=role_data["name"])
        if not role:
            role_in = RoleCreate(**role_data)
            await crud_role.create(db, obj_in=role_in)
            logger.info(f"Rol '{role_data['name']}' creado.")


async def _create_initial_superuser(db: AsyncSession):
    """Crea el superusuario inicial si no existe."""
    logger.info("Verificando y creando superusuario inicial...")
    superuser_email = settings.FIRST_SUPERUSER_EMAIL
    user = await crud_user.get_by_email(db, email=superuser_email)

    if not user:
        super_admin_role = await crud_role.get_by_name(db, name="SUPER_ADMIN")
        if not super_admin_role:
            logger.error(
                "Rol 'SUPER_ADMIN' no encontrado. No se puede crear el superusuario."
            )
            return

        user_in = UserCreate(
            email=superuser_email,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_FULL_NAME,
            role_id=super_admin_role.id,
        )
        await crud_user.create(db, obj_in=user_in)
        logger.info(
            f"Superusuario '{settings.FIRST_SUPERUSER_FULL_NAME}' creado exitosamente."
        )


async def _ensure_cosine_vector_index(conn) -> None:
    """
    Garantiza que el índice sobre `sales_vectors.embedding` use `vector_cosine_ops`.

    Las consultas RAG se ejecutan con `cosine_distance`, por lo que un índice
    creado con `vector_l2_ops` (metric incorrecta) jamás se usa. `create_all`
    no altera índices sobre tablas ya existentes, así que los entornos previos
    se corrigen aquí de forma idempotente (drop + recreate).
    """
    index_name = "idx_sales_vectors_embedding"
    row = await conn.execute(
        text(
            "SELECT indexdef FROM pg_indexes "
            "WHERE schemaname = 'public' AND indexname = :name"
        ),
        {"name": index_name},
    )
    result = row.first()
    if result and "vector_cosine_ops" in (result[0] or ""):
        return

    if result:
        logger.warning(
            "Índice %s con métrica incorrecta. Recreando con vector_cosine_ops...",
            index_name,
        )
        await conn.execute(text(f'DROP INDEX IF EXISTS "{index_name}";'))

    await conn.execute(
        text(
            f"CREATE INDEX IF NOT EXISTS \"{index_name}\" "
            "ON sales_vectors USING ivfflat (embedding vector_cosine_ops) "
            "WITH (lists = 100);"
        )
    )
    logger.info("Índice pgvector %s asegurado con vector_cosine_ops.", index_name)


async def _ensure_sales_vector_store_id(conn) -> None:
    """
    Migración idempotente: agrega la columna `store_id` a `sales_vectors`
    para poder filtrar el RAG por sucursal en bases que ya existían antes.
    """
    row = await conn.execute(
        text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'sales_vectors' AND column_name = 'store_id'"
        )
    )
    if row.first():
        return

    logger.info("Agregando columna store_id a sales_vectors (migración)...")
    await conn.execute(
        text(
            "ALTER TABLE sales_vectors "
            "ADD COLUMN store_id uuid REFERENCES stores(id) ON DELETE SET NULL;"
        )
    )
    logger.info("Columna store_id agregada a sales_vectors.")


async def _ensure_login_lock_columns(conn) -> None:
    """
    Migración idempotente: agrega las columnas de bloqueo por intentos fallidos
    de login a `users` en bases que ya existían antes.
    """
    await conn.execute(
        text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER NOT NULL DEFAULT 0;"
        )
    )
    await conn.execute(
        text(
            "ALTER TABLE users "
            "ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;"
        )
    )
    logger.info("Columnas de bloqueo de login aseguradas en users.")


async def init_db():
    """
    Initializes the database using SQLAlchemy's metadata to create all tables
    based on the defined models. This is the most robust and maintainable approach.
    """
    try:
        async with engine.begin() as conn:
            # Extensions and custom ENUM types must be handled carefully.
            # SQLAlchemy's `create_all` will create ENUMs if defined correctly in models.
            logger.info("Creating extensions...")
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "vector";'))

            logger.info("Creating database schema from models...")
            # Use run_sync to execute the synchronous `create_all` method.
            # This will create all tables, indexes, and ENUM types defined in the models.
            await conn.run_sync(Base.metadata.create_all)
            await _ensure_cosine_vector_index(conn)
            await _ensure_sales_vector_store_id(conn)
            await _ensure_login_lock_columns(conn)
            logger.info("Database schema created successfully.")

    except Exception as e:
        logger.critical(
            f"Error durante la inicialización del esquema: {e}", exc_info=True
        )
        raise

    logger.info("Starting data seeding process...")
    async with async_session_maker() as db:
        await _create_initial_roles(db)
        await _create_initial_superuser(db)
    logger.info("Data seeding process finished.")
