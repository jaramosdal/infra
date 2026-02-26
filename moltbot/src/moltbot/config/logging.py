"""Configuración de logging del proyecto."""

from __future__ import annotations

import logging
import sys

from moltbot.config.settings import settings


def setup_logging() -> None:
    """Configura el logging del proyecto según LOG_LEVEL."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )
