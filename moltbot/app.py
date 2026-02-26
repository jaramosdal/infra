"""
Moltbot — punto de entrada principal.

Escucha colas de RabbitMQ para procesar comandos de bot y facturas entrantes.
"""

from __future__ import annotations

import logging
import signal
import sys

from config import setup_logging
from database import setup_db
from rabbit import connect as connect_rabbit

import commands as _commands  # noqa: F401 — registra los handlers al importar

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Inicializa servicios y arranca el consumer loop."""
    setup_logging()
    setup_db()

    connection, channel = connect_rabbit()

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