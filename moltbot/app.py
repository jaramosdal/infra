"""
Moltbot — punto de entrada principal.

Escucha colas de RabbitMQ para procesar comandos de bot y facturas entrantes.
"""

from __future__ import annotations

import json
import logging
import signal
import sys
from typing import Callable, Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from config import settings, setup_logging
from database import setup_db, insert_factura, get_n8n_execution_count, get_total_gastos_mes
from processors.backup_manager import backup_n8n_workflows
from processors.bill_parser import get_parser
from utils.discord_bot import enviar_notificacion_factura

logger = logging.getLogger(__name__)

_rabbit = settings.rabbitmq

# ---------------------------------------------------------------------------
# Registro de comandos  (Open/Closed — añade nuevos sin tocar el dispatcher)
# ---------------------------------------------------------------------------

CommandHandler = Callable[[], str]
_COMMAND_REGISTRY: dict[str, CommandHandler] = {}


def register_command(name: str):
    """Decorador que registra un handler para un comando de texto."""

    def decorator(fn: CommandHandler) -> CommandHandler:
        _COMMAND_REGISTRY[name.lower()] = fn
        return fn

    return decorator


@register_command("!gastos")
def _cmd_gastos() -> str:
    total = get_total_gastos_mes()
    if total is not None:
        return f"💸 **Resumen de gastos de este mes:** {total:,.2f} €"
    return "⚠️ Hubo un error al consultar la base de datos."


@register_command("status_db")
def _cmd_status_db() -> str:
    count = get_n8n_execution_count()
    if count is not None:
        return f"📊 Status DB: {count} ejecuciones"
    return "⚠️ Hubo un error al consultar la base de datos."


@register_command("backup_workflows")
def _cmd_backup_workflows() -> str:
    logger.info("Iniciando backup de flujos n8n…")
    cantidad = backup_n8n_workflows()
    if cantidad is not None:
        return f"📦 Backup completado: {cantidad} flujos guardados en {settings.backup.output_folder}"
    return "⚠️ Error al realizar el backup de flujos."


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

    handler = _COMMAND_REGISTRY.get(comando)
    if handler is None:
        respuesta = f"⚠️ Comando desconocido: {comando}"
    else:
        respuesta = handler()

    ch.basic_publish(
        exchange="",
        routing_key=_rabbit.queue_respuestas,
        body=respuesta,
    )
    logger.info("Respuesta enviada: %s", respuesta)


# ---------------------------------------------------------------------------
# Conexión a RabbitMQ
# ---------------------------------------------------------------------------

def _connect_rabbit() -> tuple[pika.BlockingConnection, BlockingChannel]:
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


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Inicializa servicios y arranca el consumer loop."""
    setup_logging()
    setup_db()

    connection, channel = _connect_rabbit()

    # Graceful shutdown con SIGINT / SIGTERM
    def _shutdown(signum: int, _frame) -> None:  # noqa: ANN001
        sig_name = signal.Signals(signum).name
        logger.info("Señal %s recibida — cerrando conexión…", sig_name)
        try:
            channel.stop_consuming()
            connection.close()
        except Exception:
            pass
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logger.info("Moltbot listo. Escuchando comandos y facturas…")
    channel.start_consuming()


if __name__ == "__main__":
    main()