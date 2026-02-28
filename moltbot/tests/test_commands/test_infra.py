"""Tests de los comandos de infraestructura (status_db, backup_workflows)."""

from __future__ import annotations

from unittest.mock import patch

from moltbot.commands.infra import _cmd_backup_workflows, _cmd_status_db


class TestCmdStatusDb:
    """Tests para el comando ``status_db``."""

    @patch("moltbot.commands.infra.get_n8n_execution_count", return_value=42)
    def test_devuelve_conteo(self, mock_count) -> None:
        respuesta = _cmd_status_db()
        assert "42" in respuesta
        assert "ejecuciones" in respuesta

    @patch("moltbot.commands.infra.get_n8n_execution_count", return_value=0)
    def test_conteo_cero(self, mock_count) -> None:
        respuesta = _cmd_status_db()
        assert "0" in respuesta

    @patch("moltbot.commands.infra.get_n8n_execution_count", return_value=None)
    def test_error_db_devuelve_advertencia(self, mock_count) -> None:
        respuesta = _cmd_status_db()
        assert "error" in respuesta.lower() or "⚠️" in respuesta


class TestCmdBackupWorkflows:
    """Tests para el comando ``backup_workflows``."""

    @patch("moltbot.commands.infra.backup_n8n_workflows", return_value=5)
    def test_backup_exitoso(self, mock_backup) -> None:
        respuesta = _cmd_backup_workflows()
        assert "5" in respuesta
        assert "flujos" in respuesta.lower() or "backup" in respuesta.lower()

    @patch("moltbot.commands.infra.backup_n8n_workflows", return_value=0)
    def test_backup_cero_workflows(self, mock_backup) -> None:
        respuesta = _cmd_backup_workflows()
        assert "0" in respuesta

    @patch("moltbot.commands.infra.backup_n8n_workflows", return_value=None)
    def test_error_devuelve_advertencia(self, mock_backup) -> None:
        respuesta = _cmd_backup_workflows()
        assert "error" in respuesta.lower() or "⚠️" in respuesta
