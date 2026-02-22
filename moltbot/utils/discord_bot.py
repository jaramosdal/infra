import requests
import os

WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL_FACTURAS', 'TU_URL_AQUI')

def enviar_notificacion_factura(proveedor, importe):
    """Envía un mensaje elegante a Discord usando Webhooks"""
    
    # Formateamos el mensaje con un poco de estilo (Markdown)
    payload = {
        "content": "🔔 **Nueva Factura Detectada**",
        "embeds": [{
            "title": f"Detalle: {proveedor}",
            "color": 5814783, # Azul Iberdrola-ish
            "fields": [
                {"name": "Importe total", "value": f"**{importe} €**", "inline": True},
                {"name": "Estado", "value": "📥 Guardada en DB", "inline": True}
            ],
            "footer": {"text": "Moltbot Infrastructure"}
        }]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error enviando a Discord: {e}")