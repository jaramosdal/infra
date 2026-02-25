import pika
import os
import json
from database import setup_db, insert_factura, get_n8n_execution_count, get_total_gastos_mes
from processors.backup_manager import backup_n8n_workflows
from processors.bill_parser import extraer_importe_iberdrola, extraer_importe_totalenergies
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

def callback_facturas(ch, method, properties, body):
    try:
        # n8n envía un JSON con el texto del PDF o del cuerpo del email
        datos = json.loads(body)
        proveedor = properties.headers.get('proveedor', '') if properties.headers else 'desconocido'
        
        texto = datos.get('text', '')
        
        # Seleccionamos el procesador según el proveedor
        proveedor_lower = proveedor.lower()
        if proveedor_lower == 'totalenergies':
            importe = extraer_importe_totalenergies(texto)
        elif proveedor_lower == 'iberdrola':
            importe = extraer_importe_iberdrola(texto)
        else:
            print(f"⚠️ Proveedor desconocido: {proveedor}")
            importe = None
        
        if importe:
            # 1. Guardar en DB
            id_db = insert_factura(proveedor=proveedor, importe=importe, texto=texto[:500])
            
            # 2. Avisar a Discord
            enviar_notificacion_factura(proveedor, importe)

            print(f"✅ Factura guardada: {importe}€ (ID: {id_db})")
        else:
            print("⚠️ No se pudo extraer el importe del texto recibido")
            
    except Exception as e:
        print(f"❌ Error procesando factura: {e}")

        from database import get_total_gastos_mes # Añade este import

def callback_comandos(ch, method, properties, body):
    comando = body.decode().lower().strip()
    print(f"📩 Comando recibido: {comando}")
    
    if comando == "!gastos":
        total = get_total_gastos_mes()
        if total is not None:
            respuesta = f"💸 **Resumen de gastos de este mes:** {total:,.2f} €"
        else:
            respuesta = "⚠️ Hubo un error al consultar la base de datos."
    elif comando == "status_db":
        total = get_n8n_execution_count()
        respuesta = f"📊 Status DB: {total} ejecuciones"  
    elif comando == "backup_workflows":
        print("💾 Iniciando backup de flujos n8n...")
        cantidad = backup_n8n_workflows()
        
        if cantidad is not None:
            respuesta = f"📦 Backup completado: {cantidad} flujos guardados en /infra/n8n-workflows"
        else:
            respuesta = "⚠️ Error al realizar el backup de flujos."

    # Enviamos la respuesta a la cola de Discord
    ch.basic_publish(
        exchange='',
        routing_key='respuestas_bot',
        body=respuesta
    )

    print(f"✅ Respuesta enviada: {respuesta}")

# Escuchamos ambas colas
channel.basic_consume(queue='comandos_bot', on_message_callback=callback_comandos, auto_ack=True)
channel.basic_consume(queue='tareas_facturas', on_message_callback=callback_facturas, auto_ack=True)

print('🚀 Moltbot listo. Escuchando comandos y facturas...')
channel.start_consuming()