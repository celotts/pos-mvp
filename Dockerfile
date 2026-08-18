# Etapa 1: Builder - Instala dependencias en un entorno de construcción
# Se usa la imagen 'slim-bookworm' que ofrece un buen balance entre tamaño, compatibilidad y seguridad.
FROM python:3.11-slim-bookworm AS builder

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Actualiza los paquetes del SO e instala las dependencias de compilación.
# Se usa apt-get para Debian, se actualizan los paquetes y se limpian los cachés.
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    # Dependencias para compilar algunas librerías de Python (ej. psycopg2)
    libpq-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

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
FROM python:3.11-slim-bookworm AS runner

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala la librería cliente de PostgreSQL necesaria en tiempo de ejecución.
# Se actualizan los paquetes para instalar parches de seguridad.
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends libpq5 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia el entorno virtual desde la etapa de builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# En desarrollo, el código se monta a través de un volumen en docker-compose.
# Esta línea es crucial para producción. Crea una imagen autocontenida.
# En desarrollo, el volumen de docker-compose.override.yml sobreescribirá este código.
WORKDIR /app
COPY backend/app /app

# Copia el script de entrada desde la raíz del proyecto y lo hace ejecutable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Crea un usuario no-root para ejecutar la aplicación por seguridad
RUN addgroup --system appuser && adduser --system --ingroup appuser appuser
USER appuser

ENTRYPOINT ["/entrypoint.sh"]