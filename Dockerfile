# Etapa 1: Builder - Instala dependencias en un entorno de construcción
FROM python:3.13-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && apk upgrade && apk add --no-cache \
    build-base

WORKDIR /app
COPY backend/requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Etapa 2: Runner - La imagen final que se ejecutará
FROM python:3.13-alpine AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configura PYTHONPATH para resolver importaciones como 'from modules...' 
# Cubre tanto el código en producción (/app) como el montaje en desarrollo (/app/backend/app)
ENV PYTHONPATH="/app:/app/backend/app"

RUN apk upgrade --no-cache

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY backend/app /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN addgroup -S appuser && adduser -S -G appuser appuser
USER appuser

ENTRYPOINT ["/entrypoint.sh"]