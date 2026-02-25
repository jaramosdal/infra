"""Integración con Discord vía Webhooks."""

from __future__ import annotations

import logging

import requests

from config import settings

logger = logging.getLogger(__name__)

_discord = settings.discord


def enviar_notificacion_factura(proveedor: str, importe: float) -> bool:
    """Envía un embed a Discord notificando una nueva factura.

    Returns:
        ``True`` si el envío fue exitoso, ``False`` en caso contrario.
    """
    if not _discord.webhook_url_facturas:
        logger.warning("DISCORD_WEBHOOK_URL_FACTURAS no configurada; omitiendo envío.")
        return False

    payload = {
        "content": "🔔 **Nueva Factura Detectada**",
        "embeds": [
            {
                "title": f"Detalle: {proveedor}",
                "color": 5814783,
                "fields": [
                    {
                        "name": "Importe total",
                        "value": f"**{importe} €**",
                        "inline": True,
                    },
                    {
                        "name": "Estado",
                        "value": "📥 Guardada en DB",
                        "inline": True,
                    },
                ],
                "footer": {"text": "Moltbot Infrastructure"},
            }
        ],
    }

    try:
        response = requests.post(
            _discord.webhook_url_facturas,
            json=payload,
            timeout=_discord.request_timeout,
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        logger.exception("Error enviando notificación a Discord.")
        return False