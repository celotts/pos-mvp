# Plan de Desarrollo — API (Backend FastAPI)

## Visión general

API REST monolítica en FastAPI que da servicio al Punto de Venta: catálogo,
operación comercial (ventas/compras/inventario), analítica (market basket,
cross-selling), contabilidad y administración, con autenticación JWT,
usuarios por roles y protección de acceso.

- **Estado: completada** (uso operativo), con mejoras de seguridad en curso listas.

## Stack y estructura

```text
backend/
├── app/
│   ├── main.py                 # App FastAPI + routers (/api/v1)
│   ├── config.py               # Settings + variables de entorno
│   ├── core/                   # CRUD base, auth (JWT/SSO), seguridad (bcrypt)
│   ├── models/                 # Modelos SQLAlchemy (20 entidades)
│   ├── schemas/                # Pydantic de entrada/salida
│   ├── service/                # Lógica de negocio (crud por entidad)
│   ├── api/endpoints/          # Controllers HTTP por dominio
│   ├── dependencies.py         # Deps y guards (get_current_user, role guards)
│   ├── initial_data.py         # Seed idempotente (roles, permisos, admin)
│   └── generate_sales.py       # Datos de prueba / analítica
├── test/                       # Suite pytest (49 passed / 10 skipped)
└── script_data/                # SQL base para la BD
```

- **Base**: PostgreSQL (contenedor `pos-db`) · Host `:8003` → contenedor `:8000`.
- **ORM**: SQLAlchemy async + Pydantic v2 · **Migraciones**: seed idempotente en `initial_data.py`.

## Módulos y endpoints

### Bootstrap & Auth

| Método | Ruta | Descripción |
| --- | --- | --- |
| POST | `/api/v1/login/access-token` | Login JSON → `{access_token, user(con rol)}` |
| POST | `/api/v1/login/swagger` | Login form (doc Swagger mediante OAuth2) |
| POST | `/api/v1/login/register-superuser` | Alta de superusuario |

**Seguridad de login (implementado):**

- Máx. **3 intentos fallidos** → cuenta bloqueada (`423 Locked`, 1 hora).
- Email inexistente → `401` genérica (no revela usuarios ni cuenta intentos).
- Login correcto reinicia el contador; `PUT /users/{id}` con `is_active=true` desbloquea.
- Contraseñas con bcrypt (`core/security.py`).

### Users & Roles

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/users/` | Lista usuarios |
| GET | `/users/me` | Usuario actual con su rol |
| POST | `/users/` | Alta de usuario |
| GET | `/roles/`, `/roles/{id}` | Roles y detalle |
| PUT/POST/DELETE | `/users/{id}` | Edición, estado, baja |

### Catálogo

- **Products** `/products/*` · **Customers** `/customers/*` · **Suppliers** `/suppliers/*`
- **Stores** `/stores/*` · **Categories** (vía products) · Terminales **POS** `/terminals/*`

### Operación

- **Sales** `/sales/*` (ventas + ítems) · **Purchases** `/purchases/*` (compras + ítems, estado `COMPLETED`)
- **Shifts** `/shifts/*` · **Inventory** `/inventory/*` (stock por tienda)

### Ubicaciones

- **Countries** `/countries/*` · **States** `/states/*` · **Municipalities** `/municipalities/*` · **Specialties** `/specialties/*`

### Analítica

| Método | Ruta | Descripción |
| --- | --- | --- |
| GET | `/analytics/cross-selling?product_id=` | Recomendaciones de venta cruzada (Market Basket) |
| GET | `/analytics/market-basket` | Pares de productos más vendidos juntos |
| GET | `/analytics/…` | Más consultas de analítica (stock-out, etc.) |

### Contabilidad

- **Cash Accounts** `/cash-accounts/*` · **Accounts Payable** `/accounts-payable/*` · **Accounts Receivable** `/accounts-receivable/*`

### Asistente de IA

- `POST /assistant/…` — consultas al LLM del negocio (modelo configurable en `config.py`).

## Arquitectura de acceso

- Guard genérico por sesión JWT (`dependencies.py`).
- **RBAC por permiso (Fase 3)**: `require_permission("modulo:accion")` en controllers
  (p. ej. `sale:create`, `product:read`, `role:assign_permissions`). Catálogo de
  permisos en `initial_data.py` (`PERMISSION_CATALOG`); `SUPER_ADMIN`/`ADMIN`
  (`PROTECTED_ROLES`) tienen bypass total.
- **Multi-tenancy por `Company`** (ADR-001): `get_current_user` propaga
  `user.tenant_id` vía contextvar (`core/tenancy.py`); `crud_base`/servicios
  filtran `get/get_multi/remove` por tenant y asignan `tenant_id` en `create`.
- **Admin de roles**: CRUD de roles + asignación de permisos (solo `role:*`),
  `GET /roles/catalog/permissions` para la UI de administración.
- Respuestas unificadas: `{ success, status_code, message, data }`.

## Estado del test

| Suite                    | Resultado                             |
| ------------------------ | ------------------------------------- |
| pytest backend (`test/`) | **53 passed / 9–10 skipped / 0 failed** |

## Verificación

```bash
cd ~/develop/python/pos-mvp
podman-compose up -d              # levanta pos-db + pos-api
curl http://localhost:8003/docs   # Swagger UI
podman-compose exec -T pos-api python -m pytest test/ -q
```

- Tras cambios de código: `podman-compose restart pos-api`.
- Credenciales: `admin@posAdmin.com` / `PasswordPasAdmin123!` (rol `SUPER_ADMIN`).

## Pendiente / mejoras recomendadas

1. Documentar el resto de endpoints de `analytics_controller` (varios resúmenes aún por describir).
2. Migraciones versionadas (Alembic) en lugar del seed idempotente.
3. Paginación y filtros estandarizados en las listas.
4. Auditoría simple de operaciones sensibles (login, altas/bajas).
5. Pruebas de los endpoints de contabilidad y asistente (hoy cubiertos de forma parcial).
6. ~~Integración continua (CI) que ejecute pytest y los builds del front.~~ ✅ Hecho: GitHub Actions (pytest + ruff + build front) en verde por push.
