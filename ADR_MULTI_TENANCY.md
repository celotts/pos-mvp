# ADR-001 — Modelo de multi-tenancy (Fase 3, Paso 0)

> Estado: **Aceptado** · Fecha: 2026 · Decide: Revisión de producto/ingeniería.

## Contexto

El POS pasa a ser producto SaaS (ROADMAP H1). Hoy entidades como `products`,
`suppliers` o `users` son globales: cualquier usuario ve y opera TODO lo que hay
en la BD. Sin un límite de tenancy no hay producto ni 403 real.

## Decisión

**El tenant es `Company`** (una compañía con una o varias `stores` dentro).

- Nueva tabla `companies` (id, name, is_active, timestamps).
- `users.tenant_id` → la compañía del usuario. Un mismo rol vale en todas las
  tiendas de su compañía.
- `stores.tenant_id` → las tiendas pertenecen a una compañía.
- Catálogos del negocio (**directo en la fila**): `products`, `suppliers`,
  `customers`, `specialties`, `pos_terminals`, `cash_accounts`,
  `cash_transactions`, `accounts_payable`, `accounts_receivable` llevan
  `tenant_id` propio para scopeo lineal (sin joins) y auditoría.
- Entidades transaccionales scoped por `store_id` hoy (`sales`, `purchases`,
  `shifts`, `sales_vectors`) también reciben `tenant_id` directo, por
  uniformidad del scoping y para retirar `store_id` de las queries RAG.
- Referencias globales (sin tenant): `countries`, `states`, `municipalities`,
  y el catálogo del sistema `roles`/`permissions`.

### Alternativa descartada

Tenant = tienda directa (más rápida de construir) → migración dolorosa a
compañía después (roadmap ya la señala). Se descarta por coste de post-migración.

## Mapa de entidades (21 tablas)

| Entidad | Scoping | Columna |
| --- | --- | --- |
| companies | — (raíz) | — |
| users | directo | tenant_id |
| roles / permissions / role_permissions | sistema (global) | — |
| stores | directo | tenant_id |
| products | directo | tenant_id |
| suppliers | directo | tenant_id |
| customers | directo | tenant_id |
| specialties | directo | tenant_id |
| pos_terminals | directo | tenant_id |
| cash_accounts | directo | tenant_id |
| cash_transactions | directo | tenant_id |
| accounts_payable | directo | tenant_id |
| accounts_receivable | directo | tenant_id |
| sales / sale_items | directo (item hereda de sale) | tenant_id (sale) |
| purchases / purchase_items | directo | tenant_id (purchase) |
| shifts | directo | tenant_id |
| sales_vectors | directo | tenant_id |
| countries / states / municipalities | referencia global | — |

## Migración de tránsito

**Decisión: NO Alembic por ahora.** El código ya tiene un patrón probado de
migraciones idempotentes en `initial_data.py` (`_ensure_*` ejecutadas en
`init_db` al arranque: `ALTER ... ADD COLUMN IF NOT EXISTS`, checks contra
`information_schema`). Se reutiliza para Fase 3:

1. `create_all` crea `companies` en BD nuevas.
2. `_ensure_tenant_columns` añade `tenant_id` (nullable, FK a companies) a las
   15 tablas, idempotente, también en BD existentes con datos.
3. P1: backfill de `tenant_id` a la compañía por defecto y NOT NULL.
4. P1: re-scopeo de unicidades dentro del tenant (SKU, emails, nombres).
5. Unicidades `users.email` se mantienen globales (identidad de login).

Se adopta Alembic cuando haya múltiples entornos/refs (anotado en
DEUDA_TECNICA.md) — el salto MLE/azd lo justifica.

## Consecuencias

- Fase 3 completa: `crud_base` filtra por tenant; guard `require_permission`
  expone `user.tenant_id`; dos compañías jamás cruzan datos.
- Volumen/presupuesto: uno solo.
- La decisión es reversible a "Store directo" SIN cambios de esquema nuevos
  (bastaría setear `users.tenant_id = store_id`), lo que reduce el riesgo.