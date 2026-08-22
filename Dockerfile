# Etapa 1: Builder - Instala dependencias en un entorno de construcción
# Se usa la imagen 'alpine' que es muy ligera y tiene una superficie de ataque reducida.
FROM python:3.12-alpine AS builder

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala las dependencias de compilación para Alpine.
# Se usa apk, se actualizan los paquetes y se limpian los cachés.
# libpq-dev no es necesario ya que asyncpg no depende de la librería C de postgres.
RUN apk update && apk upgrade && apk add --no-cache \
    # Dependencias para compilar algunas librerías de Python (ej. bcrypt)
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
FROM python:3.12-alpine AS runner

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Alpine es minimalista y no necesita instalar libpq5 en runtime para asyncpg.

# Copia el entorno virtual desde la etapa de builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# En desarrollo, el código se monta a través de un volumen en docker-compose.
# Esta línea es crucial para producción. Crea una imagen autocontenida.
WORKDIR /app
COPY backend/app /app

# Copia el script de entrada desde la raíz del proyecto y lo hace ejecutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Crea un usuario no-root para ejecutar la aplicación por seguridad
RUN addgroup -S appuser && adduser -S -G appuser appuser
USER appuser

ENTRYPOINT ["/entrypoint.sh"]