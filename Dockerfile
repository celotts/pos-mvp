# Etapa 1: Builder - Instala dependencias en un entorno de construcción
FROM python:3.11-slim AS builder

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala solo las dependencias de sistema necesarias para la compilación.
# Se omite 'apt-get upgrade' para acelerar las builds de desarrollo.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requerimientos
WORKDIR /app
COPY backend/requirements.txt .

# Crea el entorno virtual y lo activa para los siguientes comandos
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala las dependencias de Python. Esto se cacheará si requirements.txt no cambia.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 2: Runner - La imagen final que se ejecutará
FROM python:3.11-slim AS runner

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala la librería de cliente de PostgreSQL necesaria en tiempo de ejecución.
# Se omite 'apt-get upgrade' para acelerar las builds de desarrollo.
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

# Copia el entorno virtual desde la etapa de builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# En desarrollo, el código se monta a través de un volumen en docker-compose.
# Esta línea se deja comentada. Se puede descomentar para construir una imagen de producción autónoma.
# COPY backend/app .

# Copia el script de entrada desde la raíz del proyecto y lo hace ejecutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Crea un usuario no-root para ejecutar la aplicación por seguridad
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser
USER appuser

ENTRYPOINT ["/entrypoint.sh"]