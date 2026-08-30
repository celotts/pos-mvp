# Deuda técnica y checklist de producción

> Propósito: registrar TODO lo que queda pendiente de cara a producción.
> **Dejar hasta el final NO rompe el desarrollo actual** — son decisiones de
> configuración/despliegue. Se marcan con prioridad y momento sugerido.

## A. Configuración que se cambia SOLO al pasar a producción

| # | Tema | Valor actual (dev) | Para producción | Dónde |
| --- | --- | --- | --- | --- |
| 1 | Expiración de token JWT | 90000 s (≈ 25 h) | 900–3600 s + **refresh token** | `core/config.py` · `core/security.py` |
| 2 | CORS | sin configurar (proxy del dev server) | Allowlist de dominios del front | `backend/app/main.py` |
| 3 | Swagger `/docs` | abierto | `docs_url=False` (o protegido con auth) | `backend/app/main.py` |
| 4 | Servidor | `--reload` + bind mount `.:/app` | `docker-compose.prod.yml` sin bind mount, sin reload, workers/gunicorn, healthcheck del API | `docker-compose.yml` |
| 5 | LLM (Ollama) | `host.containers.internal:11434` (el host) | Servicio interno/autenticado; límite de tokens por request; guard anti prompt-injection | `core/config.py` · `dependencies.py` |
| 6 | Bloqueo de login | 3 intentos / 3600 s | Ajustar según política de la empresa (1.5.2.3) | `core/config.py` |

## B. 🔴 Secreto ya publicado (lo más urgente de todo)

- [ ] `.env` está **trackeado en git** (ya está en GitHub: `celotts/pos-mvp`).
      Contiene `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD` y `SECRET_KEY`.
- [ ] Rotar credenciales: nuevo password de DB, nuevo `SECRET_KEY`, nueva password del superusuario.
- [ ] Mover `.env` a `.gitignore` y crear `.env.example` (o `.env.production`).
- [ ] Hacer que `SECRET_KEY`, `POSTGRES_PASSWORD` y `FIRST_SUPERUSER_PASSWORD`
      sean OBLIGATORIAS en producción (sin default en `core/config.py`) y que el
      app **falle al arrancar** si faltan.

> Nota: no rompe el desarrollo dejar esto al final, pero el secreto ya está
> expuesto en GitHub, así que se recomienda hacerlo cuanto antes.

## C. Mejoras estructurales (hacer en un sprint dedicado antes de producción)

| # | Tema | Beneficio | Esfuerzo |
| --- | --- | --- | --- |
| 1 | **Alembic** (migraciones versionadas) en lugar de `create_all` + parches idempotentes | Cambios de schema seguros sobre datos existentes | Medio |
| 2 | **RBAC por permiso** (tabla `permissions` + `role_permissions` + guards `can:create:sale`) en vez de solo rol admin vs no-admin | Control fino de acceso | Medio-alto |
| 3 | **Refresh token** con rotación + revocación (logout server-side / `token_version` por usuario) | Tokens comprometidos limitados a minutos | Medio |
| 4 | **Soft-delete** (`is_deleted`, `deleted_at`, `deleted_by`) + tabla `audit_log` | Datos recuperables y trazables | Medio |
| 5 | Transacciones seguras en `crud_base` (try/except + `rollback()`) y `IntegrityError` → HTTP 409 | Errores limpios, sesiones consistentes | Bajo |
| 6 | **Rate limiting** por IP en `/login` (slowapi) | Frena fuerza bruta distribuida | Bajo |
| 7 | **DB de test aislada + CI** (GitHub Actions: pytest + build front) | Evita ensuciar datos de dev; valida cada push | Medio |
| 8 | `get_llm_service` que respete `LLM_PROVIDER` (hoy hardcodea Ollama) | Coherencia con la config | Bajo |

## D. Limpieza de código al migrar (lo que NO debe ir a producción)

- [ ] `requirements.txt`: dependencias duplicadas (pytest ×2, langchain ×2) → limpiar.
- [ ] Triple inicialización de tablas (`sql/` + `script_data/` + `create_all`)
      → consolidar en un único lugar (Alembic) y eliminar duplicados.

## Criterio de aceptación para "listo para producción"

1. Secreto de `.env` rotado y fuera de git.
2. `SECRET_KEY` obligatoria sin default.
3. `docker-compose.prod.yml` desplegando la imagen construida.
4. `/docs` desactivado; CORS con allowlist.
5. Alembic con migración inicial aplicada en el entorno de producción.
6. Tests verdes y CI pasando.
7. Backup/restore de la DB verificado.
8. Usuario corriente de solo lectura para los backups (no el superusuario).
