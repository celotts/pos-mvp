#!/bin/sh

set -e

# Exportar las rutas de búsqueda para Python
# Esto garantiza que módulos en /app/backend/app y /app/backend sean visibles para todos los subprocesos
export PYTHONPATH="/app/backend/app:/app/backend:/app:${PYTHONPATH}"

# --- Iniciar la aplicación ---
echo "🚀 Iniciando el servidor Uvicorn..."

# Si se pasan argumentos desde el Dockerfile o compose (command: ...), ejecútalos
if [ "$#" -gt 0 ]; then
    exec "$@"
fi

# Comando fallback predeterminado por si no se pasa ningún 'command'
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload --app-dir /app/backend/app