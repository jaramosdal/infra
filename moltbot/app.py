import pika
import os
import time

# Sacamos los datos de conexión de las variables de entorno
user = os.getenv('RABBIT_USER', 'guest')
password = os.getenv('RABBIT_PASSWORD', 'guest')
host = 'rabbitmq' # Nombre del servicio en docker-compose

print("🤖 Moltbot está despertando...")

def conectar():
    while True:
        try:
            credentials = pika.PlainCredentials(user, password)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=host, credentials=credentials)
            )
            return connection
        except Exception as e:
            print(f"❌ Error conectando a RabbitMQ: {e}. Reintentando en 5s...")
            time.sleep(5)

connection = conectar()
channel = connection.channel()

# Creamos una cola llamada 'comandos_bot'
channel.queue_declare(queue='comandos_bot')

def callback(ch, method, properties, body):
    mensaje = body.decode()
    print(f"📩 ¡He recibido un comando!: {mensaje}")
    # Aquí es donde añadirás la lógica de tu bot más adelante
    print(f"⚙️ Procesando '{mensaje}'...")

# Le decimos a RabbitMQ que queremos escuchar la cola
channel.basic_consume(queue='comandos_bot', on_message_callback=callback, auto_ack=True)

print('🚀 Moltbot está listo y escuchando en la cola [comandos_bot].')
channel.start_consuming()