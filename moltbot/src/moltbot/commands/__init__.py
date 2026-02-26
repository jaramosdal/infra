"""
Paquete de comandos.

Importa automáticamente todos los módulos de comandos para que se registren
vía ``@register_command``. Re-exporta ``dispatch`` y ``register_command``
para uso externo.

    from moltbot.commands import dispatch, register_command
"""

from moltbot.commands.base import dispatch, register_command

# Auto-registro: importar los módulos que contienen handlers
import moltbot.commands.invoices as _invoices  # noqa: F401
import moltbot.commands.infra as _infra  # noqa: F401

__all__ = ["dispatch", "register_command"]
