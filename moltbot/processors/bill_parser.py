"""
Parsers de facturas por proveedor.

Cada proveedor implementa ``BillParser`` y se registra con ``@register_parser``.
Para añadir un nuevo proveedor basta con crear una nueva clase decorada;
no es necesario modificar el código existente (Open/Closed).
"""

from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class BillParser(ABC):
    """Interfaz común que todo parser de factura debe implementar."""

    @abstractmethod
    def extraer_importe(self, texto: str) -> Optional[float]:
        """Extrae el importe total de la factura a partir de su texto."""


# ---------------------------------------------------------------------------
# Registry de parsers  (Open/Closed)
# ---------------------------------------------------------------------------

_PARSER_REGISTRY: dict[str, type[BillParser]] = {}


def register_parser(provider: str):
    """Decorador que registra un parser para un proveedor dado (en minúsculas)."""

    def decorator(cls: type[BillParser]) -> type[BillParser]:
        _PARSER_REGISTRY[provider.lower()] = cls
        return cls

    return decorator


def get_parser(provider: str) -> Optional[BillParser]:
    """Devuelve una instancia del parser asociado al proveedor, o ``None``."""
    cls = _PARSER_REGISTRY.get(provider.lower())
    if cls is None:
        logger.warning("Proveedor desconocido: %s", provider)
        return None
    return cls()


# ---------------------------------------------------------------------------
# Utilidades compartidas (DRY)
# ---------------------------------------------------------------------------

def _parse_importe_es(raw: str) -> Optional[float]:
    """
    Convierte un string con formato numérico español (``1.170,14``) a ``float``.

    Elimina el separador de miles (punto) y sustituye la coma decimal por punto.
    """
    try:
        return float(raw.replace(".", "").replace(",", "."))
    except ValueError:
        logger.error("No se pudo convertir '%s' a número.", raw)
        return None


# ---------------------------------------------------------------------------
# Implementaciones concretas
# ---------------------------------------------------------------------------

@register_parser("iberdrola")
class IberdrolaBillParser(BillParser):
    """Parser para facturas de Iberdrola."""

    _PATTERN = re.compile(
        r"TOTAL IMPORTE FACTURA\s+([\d.,]+)\s?€", re.IGNORECASE
    )

    def extraer_importe(self, texto: str) -> Optional[float]:
        match = self._PATTERN.search(texto)
        if match:
            return _parse_importe_es(match.group(1))
        return None


@register_parser("totalenergies")
class TotalEnergiesBillParser(BillParser):
    """Parser para facturas de TotalEnergies."""

    _PATTERN_DETAILED = re.compile(
        r"Importe\s*\n\s*[\d.]+\.\d+\.\d+\s*\n\s*[^\n]+\n\s*([\d,]+)\s*€",
        re.IGNORECASE | re.DOTALL,
    )
    _PATTERN_SIMPLE = re.compile(r"([\d,]+)\s*€")

    def extraer_importe(self, texto: str) -> Optional[float]:
        match = self._PATTERN_DETAILED.search(texto)
        if match:
            return _parse_importe_es(match.group(1))

        # Fallback: último importe con formato «XXX,XX €»
        matches = self._PATTERN_SIMPLE.findall(texto)
        if matches:
            return _parse_importe_es(matches[-1])

        return None


@register_parser("o2")
class O2BillParser(BillParser):
    """Parser para facturas de O2."""

    _PATTERN = re.compile(
        r"Total factura\s+([\d.]+,\d{2})\s*€", re.IGNORECASE
    )

    def extraer_importe(self, texto: str) -> Optional[float]:
        match = self._PATTERN.search(texto)
        if match:
            return _parse_importe_es(match.group(1))
        return None


# ---------------------------------------------------------------------------
# Compatibilidad con el código existente (funciones helper)
# ---------------------------------------------------------------------------

def extraer_importe_iberdrola(texto: str) -> Optional[float]:
    """Wrapper de compatibilidad."""
    return IberdrolaBillParser().extraer_importe(texto)


def extraer_importe_totalenergies(texto: str) -> Optional[float]:
    """Wrapper de compatibilidad."""
    return TotalEnergiesBillParser().extraer_importe(texto)


def extraer_importe_o2(texto: str) -> Optional[float]:
    """Wrapper de compatibilidad."""
    return O2BillParser().extraer_importe(texto)