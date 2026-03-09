"""Configuración de logging del proyecto."""

from __future__ import annotations

import logging
import sys

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from moltbot.config.settings import settings


def setup_logging() -> None:
    """Configura el logging del proyecto según LOG_LEVEL e inicializa GlitchTip."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    # --- Inicializar Sentry SDK apuntando a GlitchTip ---
    dsn = settings.glitchtip.dsn
    if dsn:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capturar breadcrumbs desde INFO
            event_level=logging.ERROR,  # Enviar eventos a GlitchTip desde ERROR
        )
        sentry_sdk.init(
            dsn=dsn,
            integrations=[sentry_logging],
            traces_sample_rate=settings.glitchtip.traces_sample_rate,
            environment=settings.glitchtip.environment,
            release=f"moltbot@0.1.0",
        )
        logging.getLogger(__name__).info(
            "GlitchTip inicializado correctamente (environment=%s)",
            settings.glitchtip.environment,
        )
    else:
        logging.getLogger(__name__).warning(
            "GLITCHTIP_DSN no definido — los errores NO se enviarán a GlitchTip."
        )
