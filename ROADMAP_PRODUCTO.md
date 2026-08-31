# ROADMAP DE PRODUCTO — POS + IA

> Propósito: estrategia de producto para convertir el POS en algo que genere
> demanda y se diferencie, con un plan de ejecución por fases.
> Complementa a `DEUDA_TECNICA.md` (técnico) y `PLAN_DESARROLLO_API.md` (funcional).

## El producto (en una frase)

Un **POS para un nicho vertical** que no solo cobra e inventaríe: ayuda al
dueño a **no perder plata y decidir qué comprar**, primero offline y sin
fricción, y con un **Asistente de Negocio** (IA de decisiones, no un chatbot).

## Principios

1. La IA es comodity: el diferencial es convertir el dato en **decisión y acción**.
2. Los datos de negocio (montos, stock, cajas) se responden con **SQL determinista
   + tool-calling**, nunca con embeddings (evita alucinar cifras).
3. El cliente ideal es un micro-comercio (un vertical, mobile-first, offline).
4. La facturación electrónica y las integraciones locales (CFDI/DIAN/SII,
   MercadoPago) son el foso: regulación difícil + pago recurrente.
5. IA = tier premium (costo por tienda/mes, proveedor cloud configurable),
   nunca cobrar por query.

## Horizontes

### H1 — Producto vendible (hacer primero)
- [x] **Fase 3: multi-tenant + RBAC por permiso** (plan abajo).
- [ ] Mobile-first / PWA + modo offline con sincronización.
- [ ] Importación masiva de productos (Excel/CSV) — “el dolor del cambio de POS”.
- [ ] Onboarding en 5 min + reportes financieros exportables (PDF).
- [ ] Facturación electrónica y medios de pago locales (1 país primero).
- [ ] Confiabilidad: backup, auditoría, observabilidad.
- [ ] Demo grabada de 2 min (factura < 30 s + “qué necesita la tienda”) y
      pricing simple (Free ≤ X productos · Pro $X/tienda/mes · IA incluida en Pro).

### H2 — IA de decisión (el gancho de venta)
- [ ] Stockout predictivo → borrador de orden de compra.
- [ ] Resumen semanal del negocio en español (ventas, merma, top productos).
- [ ] Anomalías de caja/turnos → notificación (WhatsApp).
- [ ] Conciliación de caja vs ventas.
- [ ] Todo citado con datos reales y con permisos por tienda.

### H3 — Escala
- [ ] White-label para revendedores · métricas de retención · canales de contenido
      (build-in-public con el repo/docs).

## Fase 3 — Multi-tenant + RBAC por permiso

> Objetivo: cada tenant ve y opera SOLO sus datos; el acceso se controla por
> **permisos** (`sale:create`, `product:update`, `analytics:view`, …), no por
> rol binario. Sin esto no hay producto SaaS.

### Paso 0 — Decisión de diseño (abordar primero)
- [ ] Definir el límite de tenancy: el tenant es **Company** (con `stores`
      dentro) o **Store** directo. Decidir antes de modelar.
- [ ] Mapa de dominio: listar las 20 entidades; marcar cuáles llevan `tenant_id`
      y cuáles heredan del owner (users→stores→…).
- [ ] Decidir migración de tránsito: **Alembic** para añadir columnas con
      `tenant_id` sobre datos existentes (asignar tenant por defecto).

### Paso 1 — Datos: permisos y tenancy
- [x] Tabla `permissions` (código, descripción, módulo) y `role_permissions`.
- [x] `users.tenant_id` (y/o `store_id` scoping según Paso 0).
- [x] Añadir `tenant_id`/`store_id` a las entidades que lo requieran.
- [x] Unicidades (SKU, email, NFC) re-escopadas **dentro del tenant**.

### Paso 2 — Permisos por rol (seed idempotente en `initial_data.py`)
- [x] Catálogo base de permisos por módulo: product, sale, purchase,
      customer, supplier, inventory, shift, cash, analytics, user, assistant.
- [x] `SUPER_ADMIN` y `ADMIN` → todos los permisos.
- [x] Crear rol operativo `CASHIER` (o `SELLER`) con permisos mínimos
      (sale:create, sale:read, shift:open/close…) para que el 403 sea real.

### Paso 3 — Guard de permisos (reemplazar checks literales de rol)
- [x] Factory `require_permission("sale:create")` en `dependencies.py`.
- [x] Sustituir `role == ADMIN`/`is_admin` por guards de permiso en controllers.
- [x] `get_current_user` carga el tenant y expone `user.tenant_id`.
- [x] Scoping en `crud_base`/crud por entidad: toda query filtra por tenant.

### Paso 4 — Exposición y fin de la escalada
- [x] CRUD de roles + asignación de permisos (solo SUPER_ADMIN).
- [x] PRUEBA de la escalada: usuario CASHIER → 403 demostrable en admin-only.
- [x] Endpoints de lectura de users/analítica revertidos al permiso correspondiente.

### Paso 5 — Tests y verificación
- [x] Suite RBAC: CASHIER 403 vs ADMIN 200 vs permiso específico 200.
- [x] Suite tenancy: dos tenants no ven datos del otro (mismo seed, otra tienda).
- [x] Re-correr suite completa (unit + integración), `ruff check`, py_compile.
- [x] Extender el menú dinámico del front a permisos (hoy es por rol).

### Paso 6 — Cierre
- [ ] Actualizar docs (`PLAN_DESARROLLO_API.md`, `DEUDA_TECNICA.md` #2).
- [x] Decisiones registradas (ADR breve) sobre el modelo de tenancy.

## Criterio de aceptación de la Fase 3

1. Un usuario no-admin solo ve su tenant y solo ejecuta acciones permitidas.
2. Dos tenants con datos idénticos no se filtran información.
3. `403` reproducible con el rol CASHIER en rutas admin.
4. Suite completa en verde y sin regresiones.