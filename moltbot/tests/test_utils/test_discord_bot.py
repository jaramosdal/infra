"""Tests de las notificaciones a Discord."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest
import responses

from moltbot.utils.discord_bot import enviar_notificacion_factura

# _discord es un frozen dataclass leído al importar el módulo.
# Usamos monkeypatch sobre el atributo de módulo con un SimpleNamespace.
_DISCORD_OK = SimpleNamespace(
    webhook_url_facturas="https://discord.test/webhook",
    request_timeout=5,
)
_DISCORD_NO_URL = SimpleNamespace(
    webhook_url_facturas="",
    request_timeout=5,
)


@pytest.fixture(autouse=True)
def _patch_discord_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sustituye ``_discord`` del módulo por una config con webhook de test."""
    monkeypatch.setattr("moltbot.utils.discord_bot._discord", _DISCORD_OK)


class TestEnviarNotificacionFactura:
    """Tests para ``enviar_notificacion_factura``."""

    @responses.activate
    def test_envio_exitoso(self) -> None:
        responses.add(
            responses.POST,
            "https://discord.test/webhook",
            status=204,
        )
        result = enviar_notificacion_factura("iberdrola", 95.23)
        assert result is True
        assert len(responses.calls) == 1

    @responses.activate
    def test_payload_contiene_proveedor_e_importe(self) -> None:
        responses.add(responses.POST, "https://discord.test/webhook", status=204)
        enviar_notificacion_factura("totalenergies", 142.89)

        body = responses.calls[0].request.body
        if isinstance(body, bytes):
            body = body.decode()
        assert "totalenergies" in body
        assert "142.89" in body

    @responses.activate
    def test_payload_tiene_estructura_embed(self) -> None:
        import json

        responses.add(responses.POST, "https://discord.test/webhook", status=204)
        enviar_notificacion_factura("o2", 38.90)

        payload = json.loads(responses.calls[0].request.body)
        assert "embeds" in payload
        assert len(payload["embeds"]) == 1
        embed = payload["embeds"][0]
        assert "fields" in embed
        assert any("Importe" in f["name"] for f in embed["fields"])

    @responses.activate
    def test_error_http_devuelve_false(self) -> None:
        responses.add(
            responses.POST,
            "https://discord.test/webhook",
            status=500,
        )
        result = enviar_notificacion_factura("iberdrola", 50.0)
        assert result is False

    def test_webhook_no_configurada_devuelve_false(
        self, monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("moltbot.utils.discord_bot._discord", _DISCORD_NO_URL)
        result = enviar_notificacion_factura("iberdrola", 50.0)
        assert result is False

    @responses.activate
    def test_timeout_devuelve_false(self) -> None:
        import requests

        responses.add(
            responses.POST,
            "https://discord.test/webhook",
            body=requests.ConnectionError("timeout"),
        )
        result = enviar_notificacion_factura("iberdrola", 50.0)
        assert result is False
