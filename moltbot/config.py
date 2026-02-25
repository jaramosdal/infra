import os

# --- RabbitMQ ---
RABBIT_USER = os.getenv('RABBIT_USER', 'guest')
RABBIT_PASSWORD = os.getenv('RABBIT_PASSWORD', 'guest')
RABBIT_HOST = os.getenv('RABBIT_HOST', 'rabbitmq')

# --- PostgreSQL ---
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'n8n')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'n8n_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'n8n_password')

# --- Discord ---
DISCORD_WEBHOOK_URL_FACTURAS = os.getenv('DISCORD_WEBHOOK_URL_FACTURAS', '')
