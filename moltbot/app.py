import pika
import os
import time
import psycopg2

# Variables de entorno
RABBIT_HOST = 'rabbitmq'
POSTGRES_HOST = 'postgres'
POSTGRES_DB = os.getenv('POSTGRES_DB', 'n8n')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'n8n_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'n8n_password')

def get_db_count():
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM execution_entity;")
        count = cur.fetchone()[0]
        cur.close()
        conn.close()
        return count
    except Exception as e:
        return f"Error DB: {e}"

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

# Creamos las colas llamadas 'comandos_bot' y 'respuestas_bot'
channel.queue_declare(queue='comandos_bot')
channel.queue_declare(queue='respuestas_bot')

def callback(ch, method, properties, body):
    comando = body.decode()
    print(f"📩 Comando recibido: {comando}")
    
    if comando == "status_db":
        total = get_db_count()
        respuesta = f"📊 Reporte del sistema: Se han detectado {total} ejecuciones en la base de datos de n8n."
        
        # Enviamos la respuesta de vuelta a RabbitMQ
        ch.basic_publish(
            exchange='',
            routing_key='respuestas_bot', # Nueva cola
            body=respuesta
        )
        print(f"✅ Respuesta enviada a la cola 'respuestas_bot'")
    else:
        print(f"❓ Comando desconocido")

# Le decimos a RabbitMQ que queremos escuchar la cola
channel.basic_consume(queue='comandos_bot', on_message_callback=callback, auto_ack=True)

print('🚀 Moltbot está listo y escuchando en la cola [comandos_bot].')
channel.start_consuming()