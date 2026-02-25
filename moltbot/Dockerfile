FROM python:3.11-slim

# Dependencias de sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ejecutar como usuario no-root (seguridad)
RUN useradd --create-home moltbot
USER moltbot

CMD ["python", "-u", "app.py"]