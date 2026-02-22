import pika
import os
import json
from database import setup_db, insert_factura, get_n8n_execution_count
from processors.bill_parser import extraer_importe_iberdrola
from utils.discord_bot import enviar_notificacion_factura

# Inicializamos la base de datos
setup_db()

# Configuración RabbitMQ
RABBIT_USER = os.getenv('RABBIT_USER', 'guest')
RABBIT_PASS = os.getenv('RABBIT_PASSWORD', 'guest')
credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', credentials=credentials))
channel = connection.channel()

# Declaramos colas
channel.queue_declare(queue='comandos_bot')
channel.queue_declare(queue='tareas_facturas') 

def callback_comandos(ch, method, properties, body):
    comando = body.decode()
    if comando == "status_db":
        total = get_n8n_execution_count()
        print(f"📊 Status DB: {total} ejecuciones")
        # Aquí enviarías la respuesta de vuelta...

def callback_facturas(ch, method, properties, body):
    try:
        # n8n envía un JSON con el texto del PDF
        datos = json.loads(body)
        texto_pdf = datos.get('text', '')
        
        # Usamos el procesador modular
        importe = extraer_importe_iberdrola(texto_pdf)
        
        if importe:
            # 1. Guardar en DB
            id_db = insert_factura(proveedor="Iberdrola", importe=importe, texto=texto_pdf[:500])
            
            # 2. Avisar a Discord
            enviar_notificacion_factura("Iberdrola", importe)

            print(f"✅ Factura guardada: {importe}€ (ID: {id_db})")
        else:
            print("⚠️ No se pudo extraer el importe del texto recibido")
            
    except Exception as e:
        print(f"❌ Error procesando factura: {e}")

# Escuchamos ambas colas
channel.basic_consume(queue='comandos_bot', on_message_callback=callback_comandos, auto_ack=True)
channel.basic_consume(queue='tareas_facturas', on_message_callback=callback_facturas, auto_ack=True)

print('🚀 Moltbot listo. Escuchando comandos y facturas...')
channel.start_consuming()