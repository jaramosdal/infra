"""Tests unitarios del registro de comandos y el dispatcher."""

from __future__ import annotations

from moltbot.commands.base import dispatch, register_command


class TestRegisterCommand:
    """Verifica que ``@register_command`` registra handlers correctamente."""

    def test_registra_handler(self, clean_command_registry: dict) -> None:
        @register_command("ping")
        def _handler() -> str:
            return "pong"

        assert "ping" in clean_command_registry
        assert clean_command_registry["ping"]() == "pong"

    def test_registra_multiples_handlers(self, clean_command_registry: dict) -> None:
        @register_command("a")
        def _ha() -> str:
            return "resp_a"

        @register_command("b")
        def _hb() -> str:
            return "resp_b"

        assert len(clean_command_registry) == 2

    def test_normaliza_a_minusculas(self, clean_command_registry: dict) -> None:
        @register_command("MiComando")
        def _handler() -> str:
            return "ok"

        assert "micomando" in clean_command_registry


class TestDispatch:
    """Verifica que ``dispatch`` busca y ejecuta el handler correcto."""

    def test_comando_conocido(self, clean_command_registry: dict) -> None:
        @register_command("saludo")
        def _handler() -> str:
            return "¡Hola!"

        assert dispatch("saludo") == "¡Hola!"

    def test_comando_desconocido_devuelve_advertencia(
        self, clean_command_registry: dict
    ) -> None:
        respuesta = dispatch("inexistente")
        assert "desconocido" in respuesta.lower() or "⚠️" in respuesta

    def test_dispatch_devuelve_string(self, clean_command_registry: dict) -> None:
        @register_command("test_str")
        def _handler() -> str:
            return "resultado"

        result = dispatch("test_str")
        assert isinstance(result, str)

    def test_multiples_comandos_despachados(
        self, clean_command_registry: dict
    ) -> None:
        @register_command("uno")
        def _h1() -> str:
            return "1"

        @register_command("dos")
        def _h2() -> str:
            return "2"

        assert dispatch("uno") == "1"
        assert dispatch("dos") == "2"
