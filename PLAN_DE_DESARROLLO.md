# Plan de Desarrollo — Sistema Punto de Venta (POS)

## Visión general

Sistema POS con backend (FastAPI) y frontend (React) que cubre operación
comercial (ventas, compras, inventario, catálogo), analítica (market basket,
cross-selling, stock-out) y gestión administrativa, todo guiado por roles.

## Fase 1 — Backend (API)

**Estado: completada.** API FastAPI en `backend/`, base de datos PostgreSQL,
usuarios con roles y políticas de seguridad.

### Entregado

- Modelo de datos completo (usuarios, roles, tiendas, categorías, productos,
  proveedores, clientes, ventas, compras, inventario) en `script_data/`.
- CRUD genérico (`core/crud_base.py`) + servicios y controllers por entidad.
- Autenticación JWT (`/login/access-token`), usuarios (`/users`), roles.
- **Seguridad de login**: máximo 3 intentos fallidos → bloqueo de la cuenta
  (`423 Locked`) por 1 hora; se desbloquea al reactivar el usuario o por
  administrador.
- Rol del usuario incluido en la respuesta del login y en `GET /users/me`.
- Suite de tests: **49 passed / 10 skipped / 0 failed**.

### Verificación

```bash
cd backend
make up          # o podman-compose up -d
podman-compose exec -T pos-api python -m pytest test/ -q
```

## Fase 2 — Frontend (React)

**Estado: en curso (esqueleto y navegación listos).** Aplicación en `front/`
con Vite + React 18 + TypeScript + Tailwind CSS.

### Arquitectura

- **Menú dinámico por rol**: `front/src/menu/menu.json` define las secciones y
  los roles que pueden verlas. El sidebar y las rutas se filtran por el rol del
  usuario; acceso directo por URL a una sección no permitida → página 403.
- **Autenticación**: `AuthContext` guarda el token, restaura la sesión vía
  `/users/me` y cuenta los intentos fallidos de login (espejo del backend).
- **Rutas**: `/login`, `/dashboard` y una ruta por sección del menú generada
  desde el JSON; layout responsivo con sidebar plegable en móvil.

### Componentes

| Ruta | Componente | Estado |
| --- | --- | --- |
| `/login` | `LoginPage` | Listo (bloqueo 3 intentos integrado) |
| `/dashboard` | `DashboardPage` | Listo (resumen) |
| `/…secciones…` | `SectionPage` (placeholder de formulario) | Esqueleto |
| `/403` | `ForbiddenPage` | Listo |
| `*` | `NotFoundPage` | Listo |

### Pendiente (Fase 2)

- Reemplazar los `SectionPage` placeholder por formularios reales por módulo
  (listado + alta/edición/baja conectados a la API).
- Dashboard con métricas reales (ventas hoy, ingresos, compras, catálogo).
- Módulo de analítica: market basket, cross-selling y detección de stock-out.
- Integración con el asistente de IA del backend.

### Verificación (frontend)

```bash
cd front
npm install
npm run dev        # http://localhost:5173 (proxy /api → backend :8003)
npm run build      # typecheck + bundle de producción
```

## Credenciales de prueba

- Superusuario: `admin@posAdmin.com` / `PasswordPasAdmin123!`

## Próximos pasos

1. Formularios reales por módulo (empezar por catálogo de productos).
2. Roles de prueba `ADMIN` para validar el filtrado de menú y los 403.
3. Compatibilidad del frontend con el despliegue (variables de entorno).
