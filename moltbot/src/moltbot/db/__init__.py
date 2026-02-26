"""
Paquete de base de datos.

Re-exporta las funciones principales:

    from moltbot.db import setup_db, insert_factura
"""

from moltbot.db.engine import (
    get_n8n_execution_count,
    get_total_gastos_mes,
    get_workflows,
    insert_factura,
    setup_db,
)

__all__ = [
    "get_n8n_execution_count",
    "get_total_gastos_mes",
    "get_workflows",
    "insert_factura",
    "setup_db",
]
