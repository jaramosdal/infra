FROM python:3.11-slim

# Instalamos dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copiamos PRIMERO el archivo de requerimientos
COPY requirements.txt .

# 2. Instalamos las librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copiamos el resto del código
COPY . .

CMD ["python", "-u", "app.py"]