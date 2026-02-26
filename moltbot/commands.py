"""
Registro de comandos de Moltbot.

Define el patrón command-registry y los handlers de cada comando disponible.
Añade nuevos comandos decorando funciones con ``@register_command("nombre")``.
"""

from __future__ import annotations

import logging
from typing import Callable

from config import settings
from database import get_n8n_execution_count, get_total_gastos_mes
from processors.backup_manager import backup_n8n_workflows

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


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------

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
