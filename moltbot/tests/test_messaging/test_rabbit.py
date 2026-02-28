"""Tests de los callbacks de consumo RabbitMQ (_on_comando, _on_factura)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from moltbot.messaging.rabbit import _on_comando, _on_factura


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_properties(headers: dict | None = None) -> MagicMock:
    """Crea un mock de ``BasicProperties`` con headers opcionales."""
    props = MagicMock()
    props.headers = headers
    return props


# ======================================================================
# _on_comando
# ======================================================================

class TestOnComando:
    """Tests del callback de la cola de comandos."""

    @patch("moltbot.messaging.rabbit.dispatch", return_value="respuesta test")
    def test_publica_respuesta(self, mock_dispatch) -> None:
        ch = MagicMock()
        _on_comando(ch, MagicMock(), MagicMock(), b"ping")

        mock_dispatch.assert_called_once_with("ping")
        ch.basic_publish.assert_called_once()
        _, kwargs = ch.basic_publish.call_args
        assert kwargs["body"] == "respuesta test"

    @patch("moltbot.messaging.rabbit.dispatch", return_value="ok")
    def test_routing_key_correcto(self, mock_dispatch) -> None:
        ch = MagicMock()
        _on_comando(ch, MagicMock(), MagicMock(), b"test")

        _, kwargs = ch.basic_publish.call_args
        assert kwargs["routing_key"] == "respuestas_bot"

    @patch("moltbot.messaging.rabbit.dispatch", return_value="r")
    def test_normaliza_comando(self, mock_dispatch) -> None:
        ch = MagicMock()
        _on_comando(ch, MagicMock(), MagicMock(), b"  STATUS_DB  ")

        mock_dispatch.assert_called_once_with("status_db")


# ======================================================================
# _on_factura — happy path
# ======================================================================

class TestOnFacturaHappyPath:
    """Tests del camino feliz en el procesamiento de facturas."""

    @patch("moltbot.messaging.rabbit.enviar_notificacion_factura")
    @patch("moltbot.messaging.rabbit.insert_factura", return_value=7)
    @patch("moltbot.messaging.rabbit.get_parser")
    def test_factura_procesada_correctamente(
        self, mock_parser, mock_insert, mock_discord,
    ) -> None:
        parser_instance = MagicMock()
        parser_instance.extraer_importe.return_value = 99.50
        mock_parser.return_value = parser_instance

        body = json.dumps({"text": "TOTAL IMPORTE FACTURA 99,50 €"}).encode()
        props = _make_properties({"proveedor": "iberdrola"})

        ch = MagicMock()
        _on_factura(ch, MagicMock(), props, body)

        mock_parser.assert_called_once_with("iberdrola")
        mock_insert.assert_called_once_with(
            proveedor="iberdrola",
            importe=99.50,
            texto="TOTAL IMPORTE FACTURA 99,50 €",
        )
        mock_discord.assert_called_once_with("iberdrola", 99.50)

    @patch("moltbot.messaging.rabbit.enviar_notificacion_factura")
    @patch("moltbot.messaging.rabbit.insert_factura", return_value=1)
    @patch("moltbot.messaging.rabbit.get_parser")
    def test_texto_truncado_a_500(
        self, mock_parser, mock_insert, mock_discord,
    ) -> None:
        parser_instance = MagicMock()
        parser_instance.extraer_importe.return_value = 10.0
        mock_parser.return_value = parser_instance

        texto_largo = "A" * 1000
        body = json.dumps({"text": texto_largo}).encode()
        props = _make_properties({"proveedor": "o2"})

        _on_factura(MagicMock(), MagicMock(), props, body)

        _, kwargs = mock_insert.call_args
        assert len(kwargs["texto"]) == 500


# ======================================================================
# _on_factura — early returns
# ======================================================================

class TestOnFacturaEarlyReturns:
    """Tests de los caminos donde _on_factura retorna sin insertar."""

    @patch("moltbot.messaging.rabbit.insert_factura")
    @patch("moltbot.messaging.rabbit.get_parser", return_value=None)
    def test_parser_no_encontrado(self, mock_parser, mock_insert) -> None:
        body = json.dumps({"text": "algo"}).encode()
        props = _make_properties({"proveedor": "desconocido"})

        _on_factura(MagicMock(), MagicMock(), props, body)

        mock_insert.assert_not_called()

    @patch("moltbot.messaging.rabbit.insert_factura")
    @patch("moltbot.messaging.rabbit.get_parser")
    def test_importe_none(self, mock_parser, mock_insert) -> None:
        parser_instance = MagicMock()
        parser_instance.extraer_importe.return_value = None
        mock_parser.return_value = parser_instance

        body = json.dumps({"text": "sin importe"}).encode()
        props = _make_properties({"proveedor": "iberdrola"})

        _on_factura(MagicMock(), MagicMock(), props, body)

        mock_insert.assert_not_called()

    @patch("moltbot.messaging.rabbit.insert_factura")
    @patch("moltbot.messaging.rabbit.get_parser")
    def test_sin_headers_usa_desconocido(self, mock_parser, mock_insert) -> None:
        mock_parser.return_value = None
        body = json.dumps({"text": "algo"}).encode()
        props = _make_properties(None)  # sin headers

        _on_factura(MagicMock(), MagicMock(), props, body)

        mock_parser.assert_called_once_with("desconocido")


# ======================================================================
# _on_factura — manejo de errores
# ======================================================================

class TestOnFacturaErrores:
    """Verifica que las excepciones se capturan sin propagar."""

    def test_json_invalido_no_propaga(self) -> None:
        """Un body que no es JSON no rompe el consumidor."""
        _on_factura(MagicMock(), MagicMock(), MagicMock(), b"no es json")
        # Si llega aquí sin excepción, el try/except funciona

    @patch("moltbot.messaging.rabbit.get_parser", side_effect=RuntimeError("boom"))
    def test_excepcion_en_parser_no_propaga(self, mock_parser) -> None:
        body = json.dumps({"text": "x"}).encode()
        props = _make_properties({"proveedor": "test"})

        _on_factura(MagicMock(), MagicMock(), props, body)
        # No debe propagarse
