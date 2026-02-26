"""Comandos relacionados con facturas y gastos."""

from __future__ import annotations

import logging

from moltbot.commands.base import register_command
from moltbot.db import get_total_gastos_mes

logger = logging.getLogger(__name__)


@register_command("!gastos")
def _cmd_gastos() -> str:
    total = get_total_gastos_mes()
    if total is not None:
        return f"💸 **Resumen de gastos de este mes:** {total:,.2f} €"
    return "⚠️ Hubo un error al consultar la base de datos."
