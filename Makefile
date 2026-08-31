# Makefile para gestionar los contenedores con Docker / Podman

# Detecta si usar 'podman-compose' o 'docker compose'.
ifeq ($(shell command -v podman-compose 2> /dev/null),)
	COMPOSE_CMD ?= docker compose
else
	COMPOSE_CMD ?= podman-compose
endif

.PHONY: help up down start init clean logs ps shell lint format test test-api fix-permissions pull-models

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
	@echo "Ejecutando pruebas con pytest..."
	$(COMPOSE_CMD) exec pos-api pytest

test-api:
	@echo "Ejecutando colección de endpoints contra la BD real..."
	$(COMPOSE_CMD) exec -e TEST_API_TOKEN="$(TEST_API_TOKEN)" -e TEST_API_BASE_URL="$(TEST_API_BASE_URL)" pos-api pytest /app/backend/app/test/test_api_endpoints.py -v

fix-permissions:
	@echo "Reparando permisos de archivos para VS Code..."
	sudo chown -R $(shell whoami) .
	chmod +w .env
	@echo "¡Permisos restaurados con éxito!"