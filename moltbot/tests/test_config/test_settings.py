"""Tests unitarios para la configuración y ``_require_env``."""

from __future__ import annotations

import pytest

from moltbot.config.settings import _require_env


class TestRequireEnv:
    """Verifica que ``_require_env`` valida variables de entorno obligatorias."""

    def test_variable_existente(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TEST_VAR_OK", "valor_correcto")
        assert _require_env("TEST_VAR_OK") == "valor_correcto"

    def test_variable_inexistente_lanza_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("VARIABLE_NO_EXISTE", raising=False)
        with pytest.raises(EnvironmentError, match="obligatoria"):
            _require_env("VARIABLE_NO_EXISTE")

    def test_variable_vacia_lanza_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("VAR_VACIA", "")
        with pytest.raises(EnvironmentError, match="obligatoria"):
            _require_env("VAR_VACIA")

    def test_mensaje_incluye_nombre_variable(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MI_VAR_CUSTOM", raising=False)
        with pytest.raises(EnvironmentError, match="MI_VAR_CUSTOM"):
            _require_env("MI_VAR_CUSTOM")
