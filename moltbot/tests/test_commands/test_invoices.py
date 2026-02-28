"""Tests del comando de gastos."""

from __future__ import annotations

from unittest.mock import patch

from moltbot.commands.invoices import _cmd_gastos


class TestCmdGastos:
    """Tests para el comando ``!gastos``."""

    @patch("moltbot.commands.invoices.get_total_gastos_mes", return_value=235.50)
    def test_devuelve_total_formateado(self, mock_total) -> None:
        respuesta = _cmd_gastos()
        assert "235" in respuesta
        assert "€" in respuesta

    @patch("moltbot.commands.invoices.get_total_gastos_mes", return_value=0.0)
    def test_total_cero(self, mock_total) -> None:
        respuesta = _cmd_gastos()
        assert "0" in respuesta

    @patch("moltbot.commands.invoices.get_total_gastos_mes", return_value=None)
    def test_error_db_devuelve_advertencia(self, mock_total) -> None:
        respuesta = _cmd_gastos()
        assert "error" in respuesta.lower() or "⚠️" in respuesta

    @patch("moltbot.commands.invoices.get_total_gastos_mes", return_value=1234.56)
    def test_respuesta_es_string(self, mock_total) -> None:
        assert isinstance(_cmd_gastos(), str)
