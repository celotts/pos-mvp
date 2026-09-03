# Makefile para gestionar los contenedores con Docker / Podman

# Detecta si usar 'podman-compose' o 'docker compose'.
ifeq ($(shell command -v podman-compose 2> /dev/null),)
	COMPOSE_CMD ?= docker compose
else
	COMPOSE_CMD ?= podman-compose
endif

# Leer credenciales de BD del .env (usadas por make db-reset y db-reset-demo).
-include .env
POSTGRES_DB ?= pos_db
POSTGRES_USER ?= product
export POSTGRES_DB POSTGRES_USER

.PHONY: help up down start init clean logs ps shell lint format test test-api seed-demo fix-permissions pull-models

help:
	@echo "Comandos disponibles:"
	@echo "\n--- Gestión de Contenedores ---"
	@echo "  make up              - Levanta y reconstruye los contenedores en segundo plano."
	@echo "  make down            - Detiene contenedores, elimina redes y volúmenes (-v)."
	@echo "  make start           - Reinicio limpio: detiene, limpia el sistema y levanta todo."
	@echo "  make init            - Arranque total: levanta contenedores y descarga modelos de IA."
	@echo "  make logs            - Muestra los logs de los contenedores en tiempo real."
	@echo "  make ps              - Lista el estado actual de los contenedores."
	@echo "  make clean           - Detiene todo y limpia el sistema de artefactos (contenedores, imágenes, etc.)."
	@echo "\n--- Desarrollo, Utilidades e IA ---"
	@echo "  make pull-models     - Descarga los modelos de IA (LLM y embedding) de Ollama definidos en el .env."
	@echo "  make shell           - Inicia un shell interactivo en el contenedor de la API."
	@echo "  make lint            - Ejecuta el linter (flake8) sobre el código."
	@echo "  make format          - Formatea el código con black y isort."
	@echo "  make test            - Ejecuta las pruebas con pytest."
	@echo "  make test-api        - Ejecuta la colección de endpoints (auth, productos y Analítica) contra la BD real."
	@echo "  make seed-demo       - Siembra datos de demostración idempotentes (tienda, ventas, etc.)."
	@echo "  make db-reset        - Recrea la BD desde cero SOLO con el seed automático (sin datos demo)."
	@echo "  make db-reset-demo   - Recrea la BD y carga los datos demo de seed_demo (para probar)."
	@echo "  make fix-permissions - Corrige permisos de archivos bloqueados por Podman/Docker."
	@echo "\nUsando comando de compose: $(COMPOSE_CMD)"

up:
	@echo "Levantando los contenedores..."
	$(COMPOSE_CMD) up -d --build

down:
	@echo "Deteniendo contenedores (los volúmenes de BD se conservan)..."
	-$(COMPOSE_CMD) down --remove-orphans

start: clean up

init: up
	@echo "Esperando a que los servicios se estabilicen (5 segundos)..."
	@sleep 5
	@$(MAKE) pull-models
	@echo "¡Entorno de POS con IA inicializado correctamente!"

logs:
	@echo "Mostrando los logs de los contenedores..."
	$(COMPOSE_CMD) logs -f pos-db pos-api ollama

ps:
	@echo "Listando los contenedores..."
	$(COMPOSE_CMD) ps

clean: down
	@echo "Limpiando contenedores detenidos y caché de build..."
	@if command -v docker &> /dev/null && docker info &> /dev/null; then \
		echo "Limpiando artefactos de Docker..."; \
		docker system prune -af; \
	fi
	@if command -v podman &> /dev/null; then \
		echo "Limpiando artefactos de Podman..."; \
		podman system prune -af; \
	fi

pull-models:
	@echo "Verificando el estado del servicio Ollama..."
	@$(COMPOSE_CMD) ps ollama | grep -q "Up" || (echo "Error: El contenedor 'ollama' no está corriendo. Ejecuta 'make up' primero." && exit 1)
	@echo "Descargando modelos de IA configurados en el .env..."
	@$(COMPOSE_CMD) exec ollama sh -c "echo 'Pulling LLM model: \$$LLM_MODEL...' && ollama pull \$$LLM_MODEL"
	@$(COMPOSE_CMD) exec ollama sh -c "echo 'Pulling embedding model: \$$EMBEDDING_MODEL...' && ollama pull \$$EMBEDDING_MODEL"
	@echo "¡Modelos de IA descargados y listos para operar!"

shell:
	@echo "Iniciando shell en el contenedor pos-api..."
	$(COMPOSE_CMD) exec pos-api /bin/sh

lint:
	@echo "Ejecutando linter (flake8)..."
	$(COMPOSE_CMD) exec pos-api flake8 /app

format:
	@echo "Formateando el código con black y isort (perfil black)..."
	$(COMPOSE_CMD) exec pos-api black /app
	$(COMPOSE_CMD) exec pos-api isort --profile black /app

test:
	@echo "Ejecutando pruebas con pytest (unitarios + integración) y cobertura mínima 40%..."
	$(COMPOSE_CMD) exec -e TEST_API_BASE_URL="http://localhost:8000" pos-api pytest -q --cov=. --cov-report=term-missing --cov-fail-under=40 test

test-api:
	@echo "Ejecutando colección de endpoints contra la BD real..."
	$(COMPOSE_CMD) exec -e TEST_API_TOKEN="$(TEST_API_TOKEN)" -e TEST_API_BASE_URL="$(TEST_API_BASE_URL)" pos-api pytest /app/backend/app/test/test_api_endpoints.py -v

seed-demo:
	@echo "Sembrando datos de demostración..."
	$(COMPOSE_CMD) exec -w /app/backend/app pos-api python -m seed_demo

# Recrea la BD desde cero dejándola con ÚNICAMENTE el seed automático
# (compañía, roles, permisos y superusuario) que corre la API al arrancar.
# Útil para que la BD arranque vacía y el usuario la llene con lo que necesite.
.PHONY: db-reset
db-reset:
	@echo "Recreando la BD '$(POSTGRES_DB)' desde cero (solo seed automático)..."
	$(COMPOSE_CMD) stop pos-api
	$(COMPOSE_CMD) exec pos-db psql -P pager=off -U "$(POSTGRES_USER)" -d postgres -c \
		"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$(POSTGRES_DB)' AND pid <> pg_backend_pid();" || true
	$(COMPOSE_CMD) exec pos-db psql -P pager=off -U "$(POSTGRES_USER)" -d postgres -c "DROP DATABASE IF EXISTS $(POSTGRES_DB);"
	$(COMPOSE_CMD) exec pos-db psql -P pager=off -U "$(POSTGRES_USER)" -d postgres -c "CREATE DATABASE $(POSTGRES_DB) OWNER $(POSTGRES_USER);"
	$(COMPOSE_CMD) start pos-api
	@sleep 12
	@echo "Verificando que el esquema quedó en la revisión head de Alembic..."
	$(COMPOSE_CMD) exec -w /app/backend pos-api python -m alembic current
	@echo "BD '$(POSTGRES_DB)' recreada con seed automático (sin datos demo)."

# Deja la BD con los datos demo de seed_demo.py además del seed automático.
.PHONY: db-reset-demo
db-reset-demo:
	@$(MAKE) db-reset
	@sleep 5
	@echo "Sembrando datos de demostración..."
	$(COMPOSE_CMD) exec -w /app/backend/app pos-api python -m seed_demo
	@echo "BD lista con datos demo (tienda, proveedor, productos, clientes y ventas)."

fix-permissions:
	@echo "Reparando permisos de archivos para VS Code..."
	sudo chown -R $(shell whoami) .
	chmod +w .env
	@echo "¡Permisos restaurados con éxito!"