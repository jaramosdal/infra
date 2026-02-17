FROM python:3.11-slim

WORKDIR /app

# Instalamos la librería para RabbitMQ
RUN pip install pika

# Copiamos el código
COPY app.py .

# Por esto (el flag -u significa "unbuffered"):
CMD ["python", "-u", "app.py"]