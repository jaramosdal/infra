FROM python:3.11-slim

# Dependencias de sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar primero pyproject.toml para cachear la capa de dependencias
# 1. Copia la metadata
COPY pyproject.toml . 
# 2. Copia el código fuente
COPY src/ src/
# 3. Instala dependencias + tu paquete
RUN pip install --no-cache-dir .

# Ejecutar como usuario no-root (seguridad)
RUN useradd --create-home moltbot
USER moltbot

# 4. Arranca ejecutando __main__.py → app.main()
CMD ["python", "-u", "-m", "moltbot"]