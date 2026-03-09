"""
Paquete de configuración.

Re-exporta los símbolos principales para mantener imports cortos:

    from moltbot.config import settings, setup_logging
"""

from moltbot.config.logging import setup_logging
from moltbot.config.settings import (
    AppConfig,
    BackupConfig,
    DiscordConfig,
    GlitchTipConfig,
    PostgresConfig,
    RabbitMQConfig,
    settings,
)

__all__ = [
    "AppConfig",
    "BackupConfig",
    "DiscordConfig",
    "GlitchTipConfig",
    "PostgresConfig",
    "RabbitMQConfig",
    "settings",
    "setup_logging",
]
