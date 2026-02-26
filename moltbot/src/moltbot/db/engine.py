"""
Capa de acceso a datos de Moltbot.

Gestiona la conexión a PostgreSQL y expone funciones de consulta/inserción
para facturas, ejecuciones n8n y workflows.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator, Optional

import psycopg2
from psycopg2.extensions import connection as PgConnection

from moltbot.config import settings

logger = logging.getLogger(__name__)

_pg = settings.postgres


# ---------------------------------------------------------------------------
# Conexión
# ---------------------------------------------------------------------------

@contextmanager
def _get_connection() -> Generator[PgConnection, None, None]:
    """Abre (y cierra) una conexión a PostgreSQL de forma segura."""
    conn = psycopg2.connect(
        host=_pg.host,
        database=_pg.database,
        user=_pg.user,
        password=_pg.password,
    )
    try:
        yield conn
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def setup_db() -> None:
    """Inicializa el esquema y todas las tablas del bot."""
    queries = [
        "CREATE SCHEMA IF NOT EXISTS moltbot;",
        """
        CREATE TABLE IF NOT EXISTS moltbot.facturas_gastos (
            id SERIAL PRIMARY KEY,
            proveedor VARCHAR(50) NOT NULL,
            importe DECIMAL(10, 2) NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            texto_original TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS moltbot.logs_infraestructura (
            id SERIAL PRIMARY KEY,
            servicio VARCHAR(50) NOT NULL,
            estado VARCHAR(20) NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ]
    try:
        with _get_connection() as conn, conn.cursor() as cur:
            for q in queries:
                cur.execute(q)
            conn.commit()
            logger.info("Infraestructura 'moltbot' (facturas y servicios) lista.")
    except psycopg2.Error as exc:
        logger.exception("Error en setup_db: %s", exc)


# ---------------------------------------------------------------------------
# Facturas
# ---------------------------------------------------------------------------

def insert_factura(proveedor: str, importe: float, texto: str = "") -> Optional[int]:
    """Inserta una nueva factura y devuelve su ID, o ``None`` en caso de error."""
    query = """
        INSERT INTO moltbot.facturas_gastos (proveedor, importe, texto_original)
        VALUES (%s, %s, %s)
        RETURNING id;
    """
    try:
        importe_clean = float(str(importe).replace(",", "."))
        with _get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (proveedor, importe_clean, texto))
            factura_id: int = cur.fetchone()[0]
            conn.commit()
            return factura_id
    except (psycopg2.Error, ValueError) as exc:
        logger.exception("Error al insertar factura: %s", exc)
        return None


def get_total_gastos_mes() -> Optional[float]:
    """Suma todos los importes del mes actual."""
    query = """
        SELECT COALESCE(SUM(importe), 0)
        FROM moltbot.facturas_gastos
        WHERE date_trunc('month', fecha_registro) = date_trunc('month', CURRENT_DATE);
    """
    try:
        with _get_connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            total = cur.fetchone()[0]
            return float(total)
    except psycopg2.Error as exc:
        logger.exception("Error consultando gastos: %s", exc)
        return None


# ---------------------------------------------------------------------------
# n8n
# ---------------------------------------------------------------------------

def get_n8n_execution_count() -> Optional[int]:
    """Devuelve el número de ejecuciones registradas en n8n."""
    try:
        with _get_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM execution_entity;")
            return cur.fetchone()[0]
    except psycopg2.Error as exc:
        logger.exception("Error DB: %s", exc)
        return None


def get_workflows() -> Optional[list[tuple]]:
    """Obtiene todos los workflows de n8n (name, nodes, connections)."""
    query = "SELECT name, nodes, connections FROM workflow_entity;"
    try:
        with _get_connection() as conn, conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()
    except psycopg2.Error as exc:
        logger.exception("Error obteniendo workflows: %s", exc)
        return None
