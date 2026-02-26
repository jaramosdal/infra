"""Comandos de infraestructura y operaciones."""

from __future__ import annotations

import logging

from moltbot.commands.base import register_command
from moltbot.config import settings
from moltbot.db import get_n8n_execution_count
from moltbot.processors.backup_manager import backup_n8n_workflows

logger = logging.getLogger(__name__)


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
