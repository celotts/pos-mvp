import logging

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import settings
from core.crud_role import crud_role
from core.crud_user import crud_user
from core.db import Base, async_session_maker, engine
from models.company import Company
from models.permission import Permission
from models.role import Role

# Import all models so that Base knows about them.
# This is a crucial step to ensure that SQLAlchemy's metadata is populated
# before `Base.metadata.create_all` is called.
from schemas.role import RoleCreate
from schemas.user import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Definiciones de Datos Iniciales ---
INITIAL_ROLES = [
    {
        "name": "SUPER_ADMIN",
        "description": "Super administrador con todos los permisos.",
    },
    {"name": "ADMIN", "description": "Administrador con la mayoría de los permisos."},
    {
        "name": "CASHIER",
        "description": "Cajero: permisos mínimos operativos para la prueba de escalada.",
    },
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

        # El superusuario pertenece a la compañía por defecto (Fase 3 tenancy).
        company = (
            (await db.execute(select(Company).order_by(Company.created_at).limit(1)))
            .scalars()
            .first()
        )
        if not company:
            logger.error("Sin compañía por defecto. No se puede crear el superusuario.")
            return

        # El atributo se lee antes del commit interno de crud_user.create
        # (que expira los objetos de la sesión y dispararía lazy-load síncrono).
        company_id = company.id

        user_in = UserCreate(
            email=superuser_email,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            full_name=settings.FIRST_SUPERUSER_FULL_NAME,
            role_id=super_admin_role.id,
        )
        user = await crud_user.create(db, obj_in=user_in)
        user.tenant_id = company_id
        db.add(user)
        await db.commit()
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
            f'CREATE INDEX IF NOT EXISTS "{index_name}" '
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
        text("ALTER TABLE users ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ;")
    )
    logger.info("Columnas de bloqueo de login aseguradas en users.")


# Migración Fase 3 (multi-tenancy): tablas que llevan `tenant_id` directo.
TENANT_TABLES = [
    "users",
    "stores",
    "products",
    "suppliers",
    "customers",
    "specialties",
    "pos_terminals",
    "cash_accounts",
    "cash_transactions",
    "accounts_payable",
    "accounts_receivable",
    "sales",
    "purchases",
    "shifts",
    "sales_vectors",
]

DEFAULT_COMPANY_NAME = "Demo Company"


async def _ensure_tenant_columns(conn) -> None:
    """
    Migración idempotente (Fase 3): agrega `tenant_id` (FK a companies)
    a todas las tablas del tenant, tanto en BD nuevas como existentes.
    Se ejecuta tras `create_all` (que crea `companies` en BD nuevas).
    """
    for table in TENANT_TABLES:
        await conn.execute(
            text(
                f"ALTER TABLE {table} "
                "ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES companies(id);"
            )
        )
        await conn.execute(
            text(
                f"CREATE INDEX IF NOT EXISTS ix_{table}_tenant_id "
                f"ON {table} (tenant_id);"
            )
        )
    logger.info(
        "Columnas de multitenancy (tenant_id) aseguradas en %d tablas.",
        len(TENANT_TABLES),
    )


async def _create_default_company(db: AsyncSession) -> None:
    """Asegura que exista la compañía por defecto (idempotente)."""
    company = (
        (await db.execute(select(Company).order_by(Company.created_at).limit(1)))
        .scalars()
        .first()
    )
    if company:
        return
    db.add(Company(name=DEFAULT_COMPANY_NAME))
    await db.commit()
    logger.info("Compañía por defecto '%s' creada.", DEFAULT_COMPANY_NAME)


# --- Fase 3, P1: unicidades re-escopadas por tenant ---
# Índices únicos globales legacy (esquema de un solo tenant) que se eliminan y
# sus equivalentes compuestos (tenant_id, columna) que se crean en su lugar.
LEGACY_UNIQUE_INDEXES = [
    "ix_products_sku",
    "ix_suppliers_email",
    "ix_customers_email",
]

LEGACY_UNIQUE_CONSTRAINTS = {
    "pos_terminals": "pos_terminals_name_key",
    "specialties": "specialties_name_key",
    "cash_accounts": "cash_accounts_name_key",
}

TENANT_UNIQUE_INDEXES = [
    (
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_products_tenant_sku "
        "ON products (tenant_id, sku) WHERE sku IS NOT NULL;"
    ),
    (
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_suppliers_tenant_email "
        "ON suppliers (tenant_id, email) WHERE email IS NOT NULL;"
    ),
    (
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_customers_tenant_email "
        "ON customers (tenant_id, email) WHERE email IS NOT NULL;"
    ),
    (
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_pos_terminals_tenant_name "
        "ON pos_terminals (tenant_id, name) WHERE name IS NOT NULL;"
    ),
    (
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_specialties_tenant_name "
        "ON specialties (tenant_id, name) WHERE name IS NOT NULL;"
    ),
    (
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_cash_accounts_tenant_name "
        "ON cash_accounts (tenant_id, name) WHERE name IS NOT NULL;"
    ),
]


async def _ensure_tenant_uniqueness(conn) -> None:
    """
    Migración idempotente (Fase 3, P1): elimina las restricciones únicas globales
    de BD existentes y deja únicamente los índices únicos compuestos por tenant.
    En BD nuevas, `create_all` crea directamente los compuestos (sin globales).
    """
    for index_name in LEGACY_UNIQUE_INDEXES:
        await conn.execute(text(f'DROP INDEX IF EXISTS "{index_name}";'))
    for table, constraint_name in LEGACY_UNIQUE_CONSTRAINTS.items():
        await conn.execute(
            text(
                f'ALTER TABLE "{table}" DROP CONSTRAINT IF EXISTS "{constraint_name}";'
            )
        )
    for ddl in TENANT_UNIQUE_INDEXES:
        await conn.execute(text(ddl))
    logger.info("Unicidades re-escopadas por tenant (SKU, email, nombres) aseguradas.")


async def _backfill_tenant_id(db: AsyncSession) -> None:
    """
    Fase 3, P1: asigna la compañía por defecto a todo dato existente que aún
    no tenga tenant (migración de un solo tenant a multi-tenant). Idempotente.
    """
    company = (
        (await db.execute(select(Company).order_by(Company.created_at).limit(1)))
        .scalars()
        .first()
    )
    if not company:
        return
    company_name = company.name
    for table in TENANT_TABLES:
        await db.execute(
            text(f"UPDATE {table} SET tenant_id = :company_id WHERE tenant_id IS NULL"),
            {"company_id": company.id},
        )
    await db.commit()
    logger.info(
        "Backfill de tenant_id a '%s' aplicado a %d tablas.",
        company_name,
        len(TENANT_TABLES),
    )


# --- Fase 3, P2: catálogo de permisos por módulo (seed idempotente) ---
PERMISSION_CATALOG = {
    "product": {
        "product:create": "Crear productos",
        "product:read": "Leer productos",
        "product:update": "Actualizar productos",
        "product:delete": "Eliminar productos",
    },
    "sale": {
        "sale:create": "Registrar ventas",
        "sale:read": "Leer ventas",
        "sale:update": "Actualizar ventas",
        "sale:cancel": "Cancelar ventas",
    },
    "purchase": {
        "purchase:create": "Registrar compras",
        "purchase:read": "Leer compras",
        "purchase:update": "Actualizar compras",
        "purchase:delete": "Eliminar compras",
    },
    "customer": {
        "customer:create": "Crear clientes",
        "customer:read": "Leer clientes",
        "customer:update": "Actualizar clientes",
        "customer:delete": "Eliminar clientes",
    },
    "supplier": {
        "supplier:create": "Crear proveedores",
        "supplier:read": "Leer proveedores",
        "supplier:update": "Actualizar proveedores",
        "supplier:delete": "Eliminar proveedores",
    },
    "inventory": {
        "inventory:read": "Consultar inventario",
        "inventory:adjust": "Ajustar inventario",
    },
    "shift": {
        "shift:open": "Abrir turnos",
        "shift:close": "Cerrar turnos",
        "shift:read": "Leer turnos",
    },
    "cash": {
        "cash:create": "Registrar movimientos de caja",
        "cash:read": "Consultar caja",
        "cash:close": "Cerrar caja",
    },
    "analytics": {"analytics:read": "Consultar analítica"},
    "user": {
        "user:create": "Crear usuarios",
        "user:read": "Leer usuarios",
        "user:update": "Actualizar usuarios",
        "user:delete": "Eliminar usuarios",
    },
    "assistant": {"assistant:use": "Usar el asistente IA"},
    "store": {
        "store:create": "Crear tiendas",
        "store:read": "Leer tiendas",
        "store:update": "Actualizar tiendas",
        "store:delete": "Eliminar tiendas",
    },
    "pos_terminal": {
        "pos_terminal:create": "Crear terminales POS",
        "pos_terminal:read": "Leer terminales POS",
        "pos_terminal:update": "Actualizar terminales POS",
        "pos_terminal:delete": "Eliminar terminales POS",
    },
    "specialty": {
        "specialty:create": "Crear especialidades",
        "specialty:read": "Leer especialidades",
        "specialty:update": "Actualizar especialidades",
        "specialty:delete": "Eliminar especialidades",
    },
    "accounts": {
        "accounts:read": "Consultar cuentas por cobrar/pagar",
        "accounts:update": "Actualizar cuentas por cobrar/pagar",
        "accounts:create": "Registrar cuentas por cobrar/pagar",
        "accounts:delete": "Eliminar cuentas por cobrar/pagar",
    },
    "role": {
        "role:read": "Ver roles",
        "role:create": "Crear roles",
        "role:update": "Actualizar roles",
        "role:delete": "Eliminar roles",
        "role:assign_permissions": "Asignar permisos a roles",
        "permission:read": "Ver permisos",
    },
}

# Permisos mínimos del rol operativo CASHIER (para poder demostrar el 403).
CASHIER_PERMISSIONS = [
    "sale:create",
    "sale:read",
    "customer:create",
    "customer:read",
    "product:read",
    "inventory:read",
    "shift:open",
    "shift:close",
    "cash:create",
    "cash:read",
    "assistant:use",
]

# Roles que se mantienen al día con todo el catálogo.
FULL_ACCESS_ROLES = ["SUPER_ADMIN", "ADMIN"]


async def _ensure_permission_catalog(db: AsyncSession) -> dict[str, Permission]:
    """Asegura el catálogo de permisos (idempotente) y devuelve code -> Permission."""
    existing = {p.code: p for p in (await db.scalars(select(Permission))).all()}
    missing = [
        Permission(code=code, description=description, module=module)
        for module, codes in PERMISSION_CATALOG.items()
        for code, description in codes.items()
        if code not in existing
    ]
    if missing:
        db.add_all(missing)
        await db.flush()
        logger.info("Catálogo de permisos: %d nuevos creados.", len(missing))
        for perm in missing:
            existing[perm.code] = perm
    return existing


async def _assign_permissions_to_roles(db: AsyncSession) -> None:
    """Asigna permisos a SUPER_ADMIN/ADMIN (todo) y CASHIER (mínimos). Idempotente."""
    permission_by_code = await _ensure_permission_catalog(db)
    all_codes = list(permission_by_code)
    role_map: dict[str, list[str]] = {}
    for role_name in FULL_ACCESS_ROLES:
        role_map[role_name] = all_codes
    role_map["CASHIER"] = CASHIER_PERMISSIONS

    for role_name, codes in role_map.items():
        role = await db.scalar(
            select(Role)
            .where(Role.name == role_name)
            .options(selectinload(Role.permissions))
        )
        if not role:
            logger.warning("Rol '%s' no existe; no se asignaron permisos.", role_name)
            continue
        granted = {p.code for p in role.permissions}
        for code in codes:
            if code not in granted and code in permission_by_code:
                role.permissions.append(permission_by_code[code])
        await db.commit()
        logger.info("Rol '%s': %d permisos asegurados.", role_name, len(codes))


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
            await _ensure_tenant_columns(conn)
            await _ensure_tenant_uniqueness(conn)
            logger.info("Database schema created successfully.")

    except Exception as e:
        logger.critical(
            f"Error durante la inicialización del esquema: {e}", exc_info=True
        )
        raise

    logger.info("Starting data seeding process...")
    async with async_session_maker() as db:
        await _create_default_company(db)
        await _backfill_tenant_id(db)
        await _create_initial_roles(db)
        await _assign_permissions_to_roles(db)
        await _create_initial_superuser(db)
    logger.info("Data seeding process finished.")
