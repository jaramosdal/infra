"""Fixtures compartidas para los tests de Moltbot."""

from __future__ import annotations

from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Variables de entorno de test  (deben aplicarse ANTES de importar moltbot)
# ---------------------------------------------------------------------------

_TEST_ENV = {
    "RABBIT_USER": "test_user",
    "RABBIT_PASSWORD": "test_pass",
    "RABBIT_HOST": "localhost",
    "POSTGRES_HOST": "localhost",
    "POSTGRES_DB": "test_db",
    "POSTGRES_USER": "test_user",
    "POSTGRES_PASSWORD": "test_pass",
    "DISCORD_WEBHOOK_URL_FACTURAS": "https://discord.test/webhook",
    "DISCORD_REQUEST_TIMEOUT": "5",
    "BACKUP_OUTPUT_FOLDER": "/tmp/test-backups",
    "GLITCHTIP_DSN": "",
    "GLITCHTIP_TRACES_SAMPLE_RATE": "0.0",
    "GLITCHTIP_ENVIRONMENT": "test",
    "LOG_LEVEL": "DEBUG",
}


@pytest.fixture(autouse=True)
def _env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Establece variables de entorno de test para toda la sesión.

    Marcada como *autouse* para que ningún test toque las vars reales.
    """
    for key, value in _TEST_ENV.items():
        monkeypatch.setenv(key, value)


# ---------------------------------------------------------------------------
# Mock de la conexión a PostgreSQL
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_db_connection(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Sustituye ``_get_connection`` por un context manager que devuelve un
    ``MagicMock`` con cursor falso.  Devuelve el mock de la conexión para
    que los tests puedan configurar ``cursor().fetchone``, etc.

    Uso::

        def test_algo(mock_db_connection):
            mock_db_connection.cursor().__enter__().fetchone.return_value = (42,)
            resultado = get_total_gastos_mes()
            assert resultado == 42.0
    """
    mock_conn = MagicMock()

    @contextmanager
    def _fake_get_connection():
        yield mock_conn

    monkeypatch.setattr(
        "moltbot.db.engine._get_connection",
        _fake_get_connection,
    )
    return mock_conn


# ---------------------------------------------------------------------------
# Aislamiento de registries globales
# ---------------------------------------------------------------------------

@pytest.fixture()
def clean_command_registry(monkeypatch: pytest.MonkeyPatch) -> dict:
    """Proporciona un ``_COMMAND_REGISTRY`` limpio, aislado del global.

    Devuelve el dict vacío para que los tests puedan inspeccionarlo.
    """
    from moltbot.commands.base import _COMMAND_REGISTRY

    fresh: dict = {}
    monkeypatch.setattr("moltbot.commands.base._COMMAND_REGISTRY", fresh)
    return fresh


@pytest.fixture()
def clean_parser_registry(monkeypatch: pytest.MonkeyPatch) -> dict:
    """Proporciona un ``_PARSER_REGISTRY`` limpio, aislado del global."""
    fresh: dict = {}
    monkeypatch.setattr(
        "moltbot.processors.bill_parser._PARSER_REGISTRY",
        fresh,
    )
    return fresh
