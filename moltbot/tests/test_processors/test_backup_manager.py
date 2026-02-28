"""Tests para el módulo backup_manager: ``_sanitize_filename`` y ``backup_n8n_workflows``."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from moltbot.processors.backup_manager import _sanitize_filename, backup_n8n_workflows


class TestSanitizeFilename:
    """Garantiza que los nombres de fichero generados son seguros."""

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("Mi workflow", "Mi_workflow"),
            ("backup n8n", "backup_n8n"),
            ("simple", "simple"),
            ("con  doble  espacio", "con__doble__espacio"),
            ("ya_con_guiones_bajos", "ya_con_guiones_bajos"),
            ("con-guion-medio", "con-guion-medio"),
        ],
    )
    def test_nombres_normales(self, name: str, expected: str) -> None:
        assert _sanitize_filename(name) == expected

    @pytest.mark.parametrize(
        ("name", "expected"),
        [
            ("archivo/con/barras", "archivoconbarras"),
            ("nombre*raro?", "nombreraro"),
            ("<script>alert</script>", "scriptalertscript"),
            ('comillas"dobles', "comillasdobles"),
        ],
    )
    def test_caracteres_especiales_eliminados(self, name: str, expected: str) -> None:
        assert _sanitize_filename(name) == expected

    def test_nombre_con_tildes_y_ene(self) -> None:
        assert _sanitize_filename("Facturación año") == "Facturación_año"

    def test_string_vacio_devuelve_unnamed(self) -> None:
        assert _sanitize_filename("") == "unnamed_workflow"

    def test_solo_caracteres_especiales_devuelve_unnamed(self) -> None:
        assert _sanitize_filename("///***???") == "unnamed_workflow"

    def test_espacios_al_inicio_y_final(self) -> None:
        assert _sanitize_filename("  nombre  ") == "nombre"


# ======================================================================
# backup_n8n_workflows  (mock de get_workflows + tmp_path)
# ======================================================================

class TestBackupN8nWorkflows:
    """Tests de ``backup_n8n_workflows`` con dependencias mockeadas."""

    @patch("moltbot.processors.backup_manager.get_workflows")
    def test_exporta_workflows(self, mock_gw, tmp_path: Path) -> None:
        mock_gw.return_value = [
            ("Mi workflow", '["node1"]', '{"conn": 1}'),
            ("Otro flujo", '["node2"]', '{"conn": 2}'),
        ]
        total = backup_n8n_workflows(str(tmp_path))

        assert total == 2
        archivos = list(tmp_path.glob("*.json"))
        assert len(archivos) == 2

    @patch("moltbot.processors.backup_manager.get_workflows")
    def test_contenido_json_valido(self, mock_gw, tmp_path: Path) -> None:
        mock_gw.return_value = [
            ("Test WF", '["nodo"]', '{"c": 1}'),
        ]
        backup_n8n_workflows(str(tmp_path))

        archivo = tmp_path / "Test_WF.json"
        assert archivo.exists()
        data = json.loads(archivo.read_text(encoding="utf-8"))
        assert data["name"] == "Test WF"
        assert "nodes" in data
        assert "connections" in data

    @patch("moltbot.processors.backup_manager.get_workflows", return_value=None)
    def test_sin_workflows_devuelve_cero(self, mock_gw, tmp_path: Path) -> None:
        total = backup_n8n_workflows(str(tmp_path))
        assert total == 0

    @patch("moltbot.processors.backup_manager.get_workflows", return_value=[])
    def test_lista_vacia_devuelve_cero(self, mock_gw, tmp_path: Path) -> None:
        total = backup_n8n_workflows(str(tmp_path))
        assert total == 0

    @patch("moltbot.processors.backup_manager.get_workflows", side_effect=Exception("DB down"))
    def test_excepcion_devuelve_none(self, mock_gw, tmp_path: Path) -> None:
        total = backup_n8n_workflows(str(tmp_path))
        assert total is None

    @patch("moltbot.processors.backup_manager.get_workflows")
    def test_nombre_sanitizado_en_archivo(self, mock_gw, tmp_path: Path) -> None:
        mock_gw.return_value = [
            ("Flujo con/barras", '[]', '{}'),
        ]
        backup_n8n_workflows(str(tmp_path))
        assert (tmp_path / "Flujo_conbarras.json").exists()
