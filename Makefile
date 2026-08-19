# Makefile para gestionar los contenedores con Docker / Podman

# Detecta si usar 'podman-compose' o 'docker compose'.
ifeq ($(shell command -v podman-compose 2> /dev/null),)
	COMPOSE_CMD ?= docker compose
else
	COMPOSE_CMD ?= podman-compose
endif

.PHONY: help up down start logs ps clean shell lint format test fix-permissions

help:
	@echo "Comandos disponibles:"
	@echo "\n--- Gestión de Contenedores ---"
	@echo "  make up              - Levanta y reconstruye los contenedores en segundo plano."
	@echo "  make down            - Detiene contenedores, elimina redes y volúmenes (-v)."
	@echo "  make start           - Reinicio limpio: detiene, limpia el sistema y levanta todo."
	@echo "  make logs            - Muestra los logs de los contenedores en tiempo real."
	@echo "  make ps              - Lista el estado actual de los contenedores."
	@echo "  make clean           - Detiene todo y limpia el sistema de artefactos (contenedores, imágenes, etc.)."
	@echo "\n--- Desarrollo y Utilidades ---"
	@echo "  make shell           - Inicia un shell interactivo en el contenedor de la API."
	@echo "  make lint            - Ejecuta el linter (flake8) sobre el código."
	@echo "  make format          - Formatea el código con black y isort."
	@echo "  make test            - Ejecuta las pruebas (pendiente de implementación)."
	@echo "  make fix-permissions - Corrige permisos de archivos bloqueados por Podman/Docker."
	@echo "\nUsando comando de compose: $(COMPOSE_CMD)"

up:
	@echo "Levantando los contenedores..."
	$(COMPOSE_CMD) up -d --build

down:
	@echo "Deteniendo contenedores y eliminando volúmenes..."
	@# Se usa 'stop' explícitamente para asegurar una detención ordenada antes de eliminar.
	@# El '-' al inicio ignora errores si los contenedores ya están detenidos.
	-$(COMPOSE_CMD) stop
	-$(COMPOSE_CMD) down -v

start: clean up

logs:
	@echo "Mostrando los logs de los contenedores..."
	$(COMPOSE_CMD) logs -f

ps:
	@echo "Listando los contenedores..."
	$(COMPOSE_CMD) ps

clean: down
	@echo "Limpiando contenedores detenidos y caché de build..."
	@if command -v docker &> /dev/null; then \
		echo "Limpiando artefactos de Docker..."; \
		docker system prune -af; \
	fi
	@if command -v podman &> /dev/null; then \
		echo "Limpiando artefactos de Podman..."; \
		podman system prune -af; \
	fi

shell:
	@echo "Iniciando shell en el contenedor pos-api..."
	$(COMPOSE_CMD) exec pos-api /bin/sh

lint:
	@echo "Ejecutando linter (flake8)..."
	$(COMPOSE_CMD) exec pos-api flake8 /app

format:
	@echo "Formateando el código con black y isort..."
	$(COMPOSE_CMD) exec pos-api black /app
	$(COMPOSE_CMD) exec pos-api isort /app

test:
	@echo "Ejecutando pruebas con pytest..."
	$(COMPOSE_CMD) exec pos-api pytest

fix-permissions:
	@echo "Reparando permisos de archivos para VS Code..."
	sudo chown -R $(shell whoami) .
	chmod +w .env
	@echo "¡Permisos restaurados con éxito!"