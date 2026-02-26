"""
Capa de mensajería RabbitMQ de Moltbot.

Gestiona la conexión, declaración de colas y callbacks de consumo.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from commands import dispatch
from config import settings
from database import insert_factura
from processors.bill_parser import get_parser
from utils.discord_bot import enviar_notificacion_factura

logger = logging.getLogger(__name__)

_rabbit = settings.rabbitmq


# ---------------------------------------------------------------------------
# Callbacks de las colas
# ---------------------------------------------------------------------------

def _on_factura(
    ch: BlockingChannel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
) -> None:
    """Procesa un mensaje de la cola de facturas."""
    try:
        datos: dict = json.loads(body)
        proveedor = (
            properties.headers.get("proveedor", "desconocido")
            if properties.headers
            else "desconocido"
        )
        texto: str = datos.get("text", "")

        parser = get_parser(proveedor)
        if parser is None:
            return

        importe: Optional[float] = parser.extraer_importe(texto)

        if importe is None:
            logger.warning("No se pudo extraer el importe del texto recibido.")
            return

        id_db = insert_factura(proveedor=proveedor, importe=importe, texto=texto[:500])
        enviar_notificacion_factura(proveedor, importe)
        logger.info("Factura guardada: %.2f€ (ID: %s)", importe, id_db)

    except Exception:
        logger.exception("Error procesando factura.")


def _on_comando(
    ch: BlockingChannel,
    method: Basic.Deliver,
    properties: BasicProperties,
    body: bytes,
) -> None:
    """Procesa un comando entrante y publica la respuesta."""
    comando = body.decode().lower().strip()
    logger.info("Comando recibido: %s", comando)

    respuesta = dispatch(comando)

    ch.basic_publish(
        exchange="",
        routing_key=_rabbit.queue_respuestas,
        body=respuesta,
    )
    logger.info("Respuesta enviada: %s", respuesta)


# ---------------------------------------------------------------------------
# Conexión a RabbitMQ
# ---------------------------------------------------------------------------

def connect() -> tuple[pika.BlockingConnection, BlockingChannel]:
    """Crea la conexión y el canal a RabbitMQ, declarando las colas necesarias."""
    credentials = pika.PlainCredentials(_rabbit.user, _rabbit.password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=_rabbit.host, credentials=credentials),
    )
    channel = connection.channel()

    channel.queue_declare(queue=_rabbit.queue_comandos)
    channel.queue_declare(queue=_rabbit.queue_facturas)
    channel.queue_declare(queue=_rabbit.queue_respuestas)

    channel.basic_consume(
        queue=_rabbit.queue_comandos, on_message_callback=_on_comando, auto_ack=True,
    )
    channel.basic_consume(
        queue=_rabbit.queue_facturas, on_message_callback=_on_factura, auto_ack=True,
    )

    return connection, channel
