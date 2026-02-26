"""
Clase/protocolo base para comandos de Moltbot.

Define el registro de comandos y el dispatcher.
"""

from __future__ import annotations

import logging
from typing import Callable

logger = logging.getLogger(__name__)

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


def dispatch(comando: str) -> str:
    """Busca y ejecuta el handler para *comando*; devuelve la respuesta."""
    handler = _COMMAND_REGISTRY.get(comando)
    if handler is None:
        return f"⚠️ Comando desconocido: {comando}"
    return handler()
