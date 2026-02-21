FROM python:3.11-slim

# Necesario para que psycopg2 compile en linux slim
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalamos pika (RabbitMQ) y psycopg2 (Postgres)
RUN pip install pika psycopg2-binary

COPY app.py .

CMD ["python", "-u", "app.py"]