#!/bin/sh

set -e

# Este script ahora solo se encarga de ejecutar el comando principal del contenedor.
# La espera y la inicialización de la BD se gestionan con depends_on en docker-compose.

# --- Iniciar la aplicación ---
echo "🚀 Iniciando el servidor Uvicorn..."
exec "$@"