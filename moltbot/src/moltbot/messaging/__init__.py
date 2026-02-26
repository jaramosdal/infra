"""
Paquete de mensajería.

Re-exporta la función de conexión principal:

    from moltbot.messaging import connect
"""

from moltbot.messaging.rabbit import connect

__all__ = ["connect"]
