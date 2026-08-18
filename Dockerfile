# Etapa 1: Builder - Instala dependencias en un entorno de construcción
# Usa una imagen base Alpine para minimizar el tamaño y las vulnerabilidades.
FROM python:3.11-alpine AS builder

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Actualiza los paquetes del SO e instala las dependencias de compilación.
# 'apk add --no-cache' es la forma idiomática en Alpine.
RUN apk add --no-cache --update \
    # Dependencias para compilar algunas librerías de Python (ej. psycopg2)
    postgresql-dev \
    build-base

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
FROM python:3.11-alpine AS runner

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala la librería cliente de PostgreSQL necesaria en tiempo de ejecución.
RUN apk add --no-cache --update libpq

# Copia el entorno virtual desde la etapa de builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# En desarrollo, el código se monta a través de un volumen en docker-compose.
# Esta línea se deja comentada. Se puede descomentar para construir una imagen de producción autónoma.
WORKDIR /app
# COPY backend/app .

# Copia el script de entrada desde la raíz del proyecto y lo hace ejecutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Crea un usuario no-root para ejecutar la aplicación por seguridad
RUN addgroup -S appuser && adduser -S -G appuser appuser
USER appuser

ENTRYPOINT ["/entrypoint.sh"]