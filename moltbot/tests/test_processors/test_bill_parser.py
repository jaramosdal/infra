"""Tests unitarios para los parsers de facturas y el registry de parsers."""

from __future__ import annotations

import pytest

from moltbot.processors.bill_parser import (
    BillParser,
    IberdrolaBillParser,
    O2BillParser,
    TotalEnergiesBillParser,
    _parse_importe_es,
    get_parser,
    register_parser,
)


# ======================================================================
# _parse_importe_es  — conversión numérica formato español
# ======================================================================

class TestParseImporteEs:
    """Tests de la función auxiliar ``_parse_importe_es``."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("25,50", 25.50),
            ("1.170,14", 1170.14),
            ("1.000", 1000.0),
            ("0,99", 0.99),
            ("100", 100.0),
            ("12.345.678,90", 12345678.90),
            ("3,00", 3.0),
        ],
    )
    def test_formatos_validos(self, raw: str, expected: float) -> None:
        assert _parse_importe_es(raw) == pytest.approx(expected)

    @pytest.mark.parametrize("raw", ["abc", "", "no-numero", "€€€"])
    def test_formatos_invalidos_devuelve_none(self, raw: str) -> None:
        assert _parse_importe_es(raw) is None


# ======================================================================
# IberdrolaBillParser
# ======================================================================

class TestIberdrolaBillParser:
    """Tests del parser de Iberdrola."""

    parser = IberdrolaBillParser()

    def test_factura_tipica(self) -> None:
        texto = "...\nTOTAL IMPORTE FACTURA 95,23 €\n..."
        assert self.parser.extraer_importe(texto) == pytest.approx(95.23)

    def test_importe_con_miles(self) -> None:
        texto = "TOTAL IMPORTE FACTURA 1.170,14 €"
        assert self.parser.extraer_importe(texto) == pytest.approx(1170.14)

    def test_case_insensitive(self) -> None:
        texto = "total importe factura 50,00 €"
        assert self.parser.extraer_importe(texto) == pytest.approx(50.0)

    def test_sin_match(self) -> None:
        assert self.parser.extraer_importe("Factura de agua: 30 euros") is None

    def test_texto_vacio(self) -> None:
        assert self.parser.extraer_importe("") is None

    def test_sin_espacio_antes_euro(self) -> None:
        texto = "TOTAL IMPORTE FACTURA 42,10€"
        # El patron permite 0-1 espacio antes de €
        assert self.parser.extraer_importe(texto) == pytest.approx(42.10)


# ======================================================================
# TotalEnergiesBillParser
# ======================================================================

class TestTotalEnergiesBillParser:
    """Tests del parser de TotalEnergies."""

    parser = TotalEnergiesBillParser()

    def test_patron_simple_fallback(self) -> None:
        texto = "Resumen factura\nConsumo periodo 80,00 €\nTotal a pagar 142,89 €"
        assert self.parser.extraer_importe(texto) == pytest.approx(142.89)

    def test_unico_importe_simple(self) -> None:
        texto = "Tu factura: 55,20 €"
        assert self.parser.extraer_importe(texto) == pytest.approx(55.20)

    def test_sin_match(self) -> None:
        assert self.parser.extraer_importe("Sin importes aquí") is None

    def test_texto_vacio(self) -> None:
        assert self.parser.extraer_importe("") is None

    def test_multiples_importes_toma_ultimo(self) -> None:
        texto = "Primer concepto 20,00 €\nSegundo concepto 30,00 €\nTotal 50,00 €"
        # Fallback toma el último match
        assert self.parser.extraer_importe(texto) == pytest.approx(50.0)


# ======================================================================
# O2BillParser
# ======================================================================

class TestO2BillParser:
    """Tests del parser de O2."""

    parser = O2BillParser()

    def test_factura_tipica(self) -> None:
        texto = "Detalle de la factura\nTotal factura 38,90 €"
        assert self.parser.extraer_importe(texto) == pytest.approx(38.90)

    def test_importe_con_miles(self) -> None:
        texto = "Total factura 1.200,50 €"
        assert self.parser.extraer_importe(texto) == pytest.approx(1200.50)

    def test_case_insensitive(self) -> None:
        texto = "TOTAL FACTURA 25,00 €"
        assert self.parser.extraer_importe(texto) == pytest.approx(25.0)

    def test_sin_match(self) -> None:
        assert self.parser.extraer_importe("Resumen de consumo mensual") is None

    def test_texto_vacio(self) -> None:
        assert self.parser.extraer_importe("") is None


# ======================================================================
# Registry: get_parser / register_parser
# ======================================================================

class TestParserRegistry:
    """Tests del registro y lookup de parsers."""

    def test_get_parser_iberdrola(self) -> None:
        parser = get_parser("iberdrola")
        assert isinstance(parser, IberdrolaBillParser)

    def test_get_parser_totalenergies(self) -> None:
        parser = get_parser("totalenergies")
        assert isinstance(parser, TotalEnergiesBillParser)

    def test_get_parser_o2(self) -> None:
        parser = get_parser("o2")
        assert isinstance(parser, O2BillParser)

    def test_get_parser_case_insensitive(self) -> None:
        assert isinstance(get_parser("IBERDROLA"), IberdrolaBillParser)
        assert isinstance(get_parser("O2"), O2BillParser)

    def test_proveedor_desconocido_devuelve_none(self) -> None:
        assert get_parser("proveedor_inventado") is None

    def test_register_parser_custom(self, clean_parser_registry: dict) -> None:
        @register_parser("custom")
        class CustomParser(BillParser):
            def extraer_importe(self, texto: str):
                return 99.99

        assert "custom" in clean_parser_registry
        instance = get_parser("custom")
        assert instance is not None
        assert instance.extraer_importe("cualquier texto") == 99.99
