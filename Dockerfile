# Etapa 1: Builder - Instala dependencias en un entorno de construcción
FROM python:3.11.9-alpine3.20 AS builder

WORKDIR /app

# Instala las dependencias del sistema necesarias para compilar algunas librerías de Python
RUN apk update && apk upgrade --no-cache && apk add --no-cache \
    build-base \
    postgresql-dev

# Copia el archivo de requerimientos
COPY backend/requirements.txt .

# Instala pip y crea wheels para las dependencias. Esto acelera la construcción de la imagen final.
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /app/wheels -r requirements.txt

# Etapa 2: Runner - La imagen final que se ejecutará
FROM python:3.11.9-alpine3.20 AS runner

WORKDIR /app

# Instala solo las dependencias de sistema necesarias para ejecutar la aplicación
RUN apk update && apk upgrade --no-cache && apk add --no-cache libpq

# Copia las wheels pre-compiladas desde la etapa de builder
COPY --from=builder /app/wheels /wheels

# Instala las dependencias desde las wheels locales sin necesidad de compilarlas de nuevo
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*

# Copia el código de la aplicación
COPY backend/app .

# Crea un usuario no-root para ejecutar la aplicación por seguridad
RUN addgroup -S appgroup && adduser -S -G appgroup appuser
USER appuser